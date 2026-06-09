# Wiki Brain — Windows install
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Wiki Brain install" -ForegroundColor Cyan
Write-Host "Root: $Root"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3.12+ required. Install from https://python.org"
}

python --version

Write-Host "`nInstalling Python dependencies..."
pip install -r "$Root\mcp-server\requirements.txt"

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
    Write-Host "Created .env from .env.example — edit GITHUB_TOKEN and GITHUB_REPO if using write tools."
} else {
    Write-Host ".env already exists — skipped."
}

Write-Host "`nRunning tests..."
$env:WIKI_BRAIN_DIR = "$Root\wiki"
python "$Root\mcp-server\test_server.py"

Write-Host "`nDone. Start server: .\scripts\start.ps1" -ForegroundColor Green
