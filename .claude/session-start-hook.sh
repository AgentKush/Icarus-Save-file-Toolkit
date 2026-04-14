#!/bin/bash
# Session Start Hook: Bootstrap plugins for Claude Code web sessions
# Calls the shared setup script from the repo root
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
bash "$SCRIPT_DIR/claude-setup.sh" 2>/dev/null || true
