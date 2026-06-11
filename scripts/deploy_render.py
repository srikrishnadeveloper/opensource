#!/usr/bin/env python3
"""Deploy Wiki Brain to Render via API and print the ChatGPT MCP URL.

Requires:
  RENDER_API_KEY in .env or environment (Render Dashboard → Account → API Keys)

Optional .env:
  GITHUB_REPO   (default: srikrishnadeveloper/opensource)
  GITHUB_BRANCH (default: main)

Run from repo root:
  python scripts/deploy_render.py
"""
from __future__ import annotations

import json
import os
import secrets
import sys
import time
from pathlib import Path
from urllib.parse import quote

import httpx

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.render.com/v1"
SERVICE_NAME = "wiki-brain-mcp"
DEFAULT_REPO = "srikrishnadeveloper/opensource"
DEFAULT_BRANCH = "main"


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def api_key() -> str:
    key = os.environ.get("RENDER_API_KEY", "").strip()
    if not key:
        print(
            "RENDER_API_KEY is not set.\n"
            "Add it to .env or Cloud Agent secrets, then rerun:\n"
            "  RENDER_API_KEY=rnd_... python scripts/deploy_render.py",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def client() -> httpx.Client:
    return httpx.Client(
        base_url=API,
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=60.0,
    )


def _unwrap(item: dict, key: str) -> dict:
    """Render list endpoints wrap records as {cursor, service|owner|...}."""
    return item.get(key) or item


def owner_id(c: httpx.Client) -> str:
    r = c.get("/owners")
    r.raise_for_status()
    owners = r.json()
    if not owners:
        raise RuntimeError("No Render workspaces found for this API key")
    owner = _unwrap(owners[0], "owner")
    print(f"Using workspace: {owner.get('name', owner['id'])}")
    return owner["id"]


def find_service(c: httpx.Client, owner: str) -> dict | None:
    r = c.get("/services", params={"ownerId": owner, "name": SERVICE_NAME, "limit": 20})
    r.raise_for_status()
    for item in r.json():
        svc = _unwrap(item, "service")
        if svc.get("name") == SERVICE_NAME:
            return svc
    return None


def update_service(c: httpx.Client, service_id: str, repo: str, branch: str) -> None:
    payload = {
        "repo": f"https://github.com/{repo}",
        "branch": branch,
        "serviceDetails": {
            "healthCheckPath": "/health",
            "envSpecificDetails": {"dockerfilePath": "./Dockerfile"},
        },
    }
    r = c.patch(f"/services/{service_id}", json=payload)
    if r.status_code >= 400:
        raise RuntimeError(f"Update service failed ({r.status_code}): {r.text[:500]}")
    print(f"Updated service repo={repo} branch={branch}")


def ensure_env_vars(c: httpx.Client, service_id: str) -> str:
    """Set required env vars; return MCP_API_KEY (create if missing)."""
    required = {
        "WIKI_BRAIN_DIR": "/app/wiki",
        "MCP_TRANSPORT": "streamable-http",
        "PORT": "8000",
    }
    mcp_key = env_var_value(c, service_id, "MCP_API_KEY")
    if not mcp_key:
        mcp_key = secrets.token_urlsafe(32)
        required["MCP_API_KEY"] = mcp_key
        print("Generated new MCP_API_KEY for Render service")
    for key, value in required.items():
        r = c.put(f"/services/{service_id}/env-vars/{key}", json={"value": value})
        if r.status_code >= 400:
            raise RuntimeError(f"Set env {key} failed ({r.status_code}): {r.text[:300]}")
    return mcp_key


def create_service(c: httpx.Client, owner: str, repo: str, branch: str) -> dict:
    mcp_key = secrets.token_urlsafe(32)
    payload = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": owner,
        "repo": f"https://github.com/{repo}",
        "branch": branch,
        "autoDeploy": "yes",
        "serviceDetails": {
            "runtime": "docker",
            "plan": "free",
            "healthCheckPath": "/health",
            "envSpecificDetails": {"dockerfilePath": "./Dockerfile"},
        },
        "envVars": [
            {"key": "WIKI_BRAIN_DIR", "value": "/app/wiki"},
            {"key": "MCP_TRANSPORT", "value": "streamable-http"},
            {"key": "PORT", "value": "8000"},
            {"key": "MCP_API_KEY", "value": mcp_key},
        ],
    }
    r = c.post("/services", json=payload)
    if r.status_code >= 400:
        raise RuntimeError(f"Create service failed ({r.status_code}): {r.text[:500]}")
    svc = r.json().get("service") or r.json()
    print(f"Created service {SERVICE_NAME} ({svc['id']})")
    return svc


def trigger_deploy(c: httpx.Client, service_id: str) -> str:
    r = c.post(f"/services/{service_id}/deploys", json={"clearCache": "do_not_clear"})
    if r.status_code >= 400:
        r = c.post(f"/services/{service_id}/deploys", json={})
    r.raise_for_status()
    deploy = _unwrap(r.json(), "deploy")
    deploy_id = deploy["id"]
    print(f"Deploy started: {deploy_id}")
    return deploy_id


def wait_deploy(c: httpx.Client, service_id: str, deploy_id: str, timeout_s: int = 900) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        r = c.get(f"/services/{service_id}/deploys/{deploy_id}")
        r.raise_for_status()
        deploy = _unwrap(r.json(), "deploy")
        status = deploy.get("status", "unknown")
        print(f"  deploy status: {status}")
        if status == "live":
            return
        if status in ("build_failed", "update_failed", "canceled", "deactivated"):
            raise RuntimeError(f"Deploy failed with status: {status}")
        time.sleep(15)
    raise TimeoutError("Deploy timed out")


def service_url(c: httpx.Client, service_id: str) -> str:
    r = c.get(f"/services/{service_id}")
    r.raise_for_status()
    svc = _unwrap(r.json(), "service")
    details = svc.get("serviceDetails") or {}
    url = (details.get("url") or "").rstrip("/")
    if not url:
        slug = svc.get("slug") or SERVICE_NAME
        url = f"https://{slug}.onrender.com"
    return url


def env_var_value(c: httpx.Client, service_id: str, key: str) -> str | None:
    r = c.get(f"/services/{service_id}/env-vars")
    r.raise_for_status()
    for item in r.json():
        ev = _unwrap(item, "envVar")
        if ev.get("key") == key:
            return ev.get("value")
    return None


def test_health(base_url: str, mcp_key: str) -> None:
    with httpx.Client(timeout=60.0, follow_redirects=True) as h:
        health = h.get(f"{base_url}/health", headers={"Authorization": f"Bearer {mcp_key}"})
        print(f"Health: {health.status_code} {health.text[:200]}")
        health.raise_for_status()

        init = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "deploy-render", "version": "1.0"},
            },
        }
        mcp_url = f"{base_url}/mcp?token={quote(mcp_key)}"
        r = h.post(
            mcp_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            json=init,
        )
        print(f"MCP initialize: {r.status_code}")
        r.raise_for_status()


def main() -> None:
    load_dotenv()
    repo = os.environ.get("GITHUB_REPO", DEFAULT_REPO).strip() or DEFAULT_REPO
    branch = os.environ.get("GITHUB_BRANCH", DEFAULT_BRANCH).strip() or DEFAULT_BRANCH

    with client() as c:
        owner = owner_id(c)
        svc = find_service(c, owner)
        if svc:
            print(f"Found existing service: {svc['id']}")
            update_service(c, svc["id"], repo, branch)
        else:
            svc = create_service(c, owner, repo, branch)

        service_id = svc["id"]
        ensure_env_vars(c, service_id)
        deploy_id = trigger_deploy(c, service_id)
        wait_deploy(c, service_id, deploy_id)

        base = service_url(c, service_id)
        mcp_key = env_var_value(c, service_id, "MCP_API_KEY")
        if not mcp_key:
            raise RuntimeError("MCP_API_KEY not found on Render service")

        print("\nWaiting for service to accept traffic...")
        time.sleep(10)
        test_health(base, mcp_key)

        chatgpt_url = f"{base}/mcp?token={mcp_key}"
        print("\n" + "=" * 72)
        print("  WIKI BRAIN — ChatGPT connector URL")
        print(f"\n  {chatgpt_url}\n")
        print("  Paste into ChatGPT → Settings → Connectors → Add MCP server.")
        print("=" * 72)

        # Update local .env for smoke tests (do not commit)
        env_path = ROOT / ".env"
        lines: list[str] = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
        updates = {
            "RENDER_API_KEY": os.environ.get("RENDER_API_KEY", ""),
            "MCP_TEST_URL": base,
            "MCP_API_KEY": mcp_key,
        }
        present = {line.split("=", 1)[0].strip() for line in lines if "=" in line and not line.strip().startswith("#")}
        for key, value in updates.items():
            if not value:
                continue
            new_line = f"{key}={value}"
            replaced = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = new_line
                    replaced = True
                    break
            if not replaced:
                lines.append(new_line)
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nSaved MCP_TEST_URL and MCP_API_KEY to {env_path}")


if __name__ == "__main__":
    main()
