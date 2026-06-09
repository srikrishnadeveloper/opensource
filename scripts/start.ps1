# Wiki Brain — start MCP server (stdio, for Cursor / Claude Desktop)
$Root = Split-Path -Parent $PSScriptRoot
$env:WIKI_BRAIN_DIR = if ($env:WIKI_BRAIN_DIR) { $env:WIKI_BRAIN_DIR } else { "$Root\wiki" }
$env:MCP_TRANSPORT = if ($env:MCP_TRANSPORT) { $env:MCP_TRANSPORT } else { "stdio" }

# Load .env if present (simple KEY=VALUE parser)
$envFile = Join-Path $Root ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $k = $matches[1].Trim()
            $v = $matches[2].Trim()
            if ($v) { Set-Item -Path "env:$k" -Value $v }
        }
    }
}

Write-Host "Wiki Brain MCP — WIKI_BRAIN_DIR=$env:WIKI_BRAIN_DIR transport=$env:MCP_TRANSPORT"
python "$Root\mcp-server\server.py"
