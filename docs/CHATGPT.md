# Connect Wiki Brain to ChatGPT

ChatGPT connects to MCP servers over **HTTP** (not stdio). Deploy Wiki Brain to Render, then add it as a custom connector.

## Prerequisites

- Render account (free tier works)
- GitHub fork of this repo
- Strong `MCP_API_KEY` (random 32+ char string)

## 1. Deploy to Render

### Option A — Blueprint

1. Push this `opensource/` folder to your GitHub repo
2. Render → **New** → **Blueprint** → connect repo
3. Render reads `render.yaml` automatically

### Option B — Manual

1. New **Web Service** → Docker
2. Dockerfile path: `./Dockerfile`
3. Set environment variables (see below)

## 2. Environment variables on Render

| Variable | Required | Example |
|----------|----------|---------|
| `MCP_API_KEY` | Yes | random secret string |
| `MCP_TRANSPORT` | Yes | `streamable-http` (set in Dockerfile) |
| `GITHUB_TOKEN` | For writes | fine-grained PAT |
| `GITHUB_REPO` | For writes | `you/wiki-brain` |
| `GITHUB_BRANCH` | For writes | `main` |

After deploy, note your URL: `https://wiki-brain-mcp-xxxx.onrender.com`

## 3. Health check

```bash
curl https://YOUR-SERVICE.onrender.com/health
```

Expected: `{"status":"ok","service":"wiki-brain",...}`

## 4. Add ChatGPT connector

1. ChatGPT → **Settings** → **Connectors** (or Developer / MCP section)
2. Add MCP server URL:

```
https://YOUR-SERVICE.onrender.com/mcp
```

3. Authentication: **Bearer token** = your `MCP_API_KEY`

   If the UI only supports query auth:

```
https://YOUR-SERVICE.onrender.com/mcp?token=YOUR_MCP_API_KEY
```

4. Save and enable the connector in a new chat

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 Unauthorized | Check `MCP_API_KEY` matches Render env |
| Empty search results | Redeploy after pushing wiki changes to GitHub |
| Write tools fail | Set `GITHUB_TOKEN` + `GITHUB_REPO` on Render |
| Cold start slow | Free tier sleeps after inactivity — first request wakes it |
