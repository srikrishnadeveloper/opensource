# Deploy on Render (simple)

Wiki Brain on Render is designed so you **deploy first** and **paste one optional key** — everything else is automatic.

## 3-step flow

### 1. Fork + deploy

1. **Fork** this repository on GitHub.
2. Open [Render Dashboard](https://dashboard.render.com/) → **New +** → **Blueprint**.
3. Connect **your fork**. Render reads `render.yaml` and creates the service.

You do **not** need to set `MCP_API_KEY`, `GITHUB_REPO`, or `GITHUB_BRANCH` — Render handles those.

### 2. (Optional) Enable wiki writes

Only if you want ChatGPT/Cursor to **create or edit** wiki pages in the cloud:

1. Create a [fine-grained GitHub PAT](GITHUB.md) (Contents: read+write on your fork).
2. Render → your service → **Environment** → add:
   - `GITHUB_TOKEN` = your PAT

Repo and branch are detected automatically from your connected GitHub repo.

**Read-only?** Skip this step — search and `read_page` work with zero secrets.

### 3. Connect ChatGPT

1. Render → your service → **Logs**.
2. Find the startup banner that looks like:

```
========================================================================
  WIKI BRAIN — ChatGPT connector (copy the line below)

  https://YOUR-SERVICE.onrender.com/mcp?token=...

  Paste into ChatGPT → Settings → Connectors → Add MCP server.
========================================================================
```

3. Copy that **full URL** into ChatGPT → **Settings** → **Connectors**.

Done. Ask ChatGPT: *"Search my wiki for task tracker"*.

---

## What Render configures automatically

| Setting | How |
|---------|-----|
| `MCP_API_KEY` | Random secret (`generateValue: true` in `render.yaml`) |
| `GITHUB_REPO` | `RENDER_GIT_REPO_SLUG` (your fork, e.g. `you/opensource`) |
| `GITHUB_BRANCH` | `RENDER_GIT_BRANCH` (deploy branch, usually `main`) |
| `MCP_TRANSPORT` | `streamable-http` |
| ChatGPT URL | Printed in **Logs** on every deploy/restart |

## One-click deploy button

From the repo README:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/srikrishnadeveloper/opensource)

(Use your fork URL after forking.)

## Service details

- **Runtime:** Docker (`Dockerfile`)
- **Port:** 8000
- **Health:** `/health`
- **MCP endpoint:** `/mcp`

## Updating wiki content

The Docker image includes `wiki/` at **build** time. To refresh read-only content:

1. Push markdown changes to GitHub.
2. Render auto-redeploys (or trigger **Manual Deploy**).

With `GITHUB_TOKEN` set, write tools commit to GitHub immediately — no redeploy needed for those edits.

## Custom domain (optional)

Render → **Settings** → **Custom Domains** — use your domain in the ChatGPT connector URL instead of `onrender.com`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No URL in logs | Wait for deploy to finish; check **Logs** tab (not Build logs) |
| 401 on ChatGPT | Copy the **full** URL from logs (includes `?token=`) |
| Write tools fail | Add `GITHUB_TOKEN` with Contents read+write on your fork |
| Cold start slow | Free tier sleeps — first request may take ~30s |
