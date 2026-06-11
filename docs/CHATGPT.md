# Connect Wiki Brain to ChatGPT

ChatGPT talks to MCP servers over **HTTP**. Deploy Wiki Brain to Render, then paste **one URL** from the Render logs.

## Prerequisites

- A [Render](https://render.com) account (free tier works)
- A GitHub fork of this repo
- (Optional) GitHub PAT — only for **write** tools

## Setup (2 minutes)

### 1. Deploy to Render

Follow **[docs/RENDER.md](RENDER.md)** — fork, Blueprint deploy, done.

You do **not** manually invent an API key or repo name.

### 2. Copy URL from Render logs

After deploy, open **Render → your service → Logs**.

Look for:

```
  WIKI BRAIN — ChatGPT connector (copy the line below)

  https://wiki-brain-mcp-xxxx.onrender.com/mcp?token=YOUR_AUTO_GENERATED_KEY
```

Copy that entire line.

### 3. Add ChatGPT connector

1. ChatGPT → **Settings** → **Connectors** (or Developer / MCP)
2. **Add MCP server**
3. Paste the URL from Render logs
4. Save and enable the connector in a new chat

Test: *"Search my wiki for mongodb"* or *"What's in my task tracker project?"*

## Optional: enable writes

To let ChatGPT **edit** your wiki in the cloud:

1. Create a fine-grained PAT — [docs/GITHUB.md](GITHUB.md)
2. Render → **Environment** → `GITHUB_TOKEN` = your PAT
3. **Restart** the service (or wait for redeploy)
4. Logs will show `Wiki writes: enabled`

## Authentication notes

| Method | When |
|--------|------|
| `?token=` in URL | Easiest — included in the log banner (ChatGPT-friendly) |
| `Authorization: Bearer …` | If the connector UI supports custom headers |

The token is the auto-generated `MCP_API_KEY` — you never type it yourself; copy it from logs.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 Unauthorized | Use the full URL from Render logs, including `?token=` |
| Empty search | Wiki is baked at build time — push changes to GitHub and redeploy |
| Write tools fail | Set `GITHUB_TOKEN` on Render |
| Slow first message | Free tier cold start — retry after ~30 seconds |
