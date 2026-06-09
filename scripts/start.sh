#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export WIKI_BRAIN_DIR="${WIKI_BRAIN_DIR:-$ROOT/wiki}"
export MCP_TRANSPORT="${MCP_TRANSPORT:-stdio}"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source <(grep -v '^\s*#' "$ROOT/.env" | grep -v '^\s*$' | sed 's/^/export /')
  set +a
fi

echo "Wiki Brain MCP — WIKI_BRAIN_DIR=$WIKI_BRAIN_DIR transport=$MCP_TRANSPORT"
exec python3 "$ROOT/mcp-server/server.py"
