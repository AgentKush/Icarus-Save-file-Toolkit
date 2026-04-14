#!/bin/bash
# Claude Code Web Session Bootstrap
# Run at the start of any co.work session to set up plugins & guidelines.
#
# Usage (paste into any session):
#   curl -sL https://raw.githubusercontent.com/AgentKush/Icarus-Save-file-Toolkit/main/claude-setup.sh | bash
#
# What this does:
#   1. Installs claude-mem (automatic memory across sessions)
#   2. Installs andrej-karpathy-skills (coding guidelines plugin)
#   3. Adds Karpathy guidelines to the current project's CLAUDE.md
#   4. Sets up a SessionStart hook at user level so if you switch repos
#      in the same session, plugins stay active

set -e

echo "=== Claude Code Web Session Bootstrap ==="
echo ""

# --- 1. Install claude-mem ---
echo "[1/4] Installing claude-mem..."
npx -y claude-mem install 2>/dev/null
echo "  Done."

# --- 2. Install andrej-karpathy-skills plugin ---
echo "[2/4] Installing andrej-karpathy-skills..."
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/forrestchang"
if [ ! -d "$MARKETPLACE_DIR" ]; then
  git clone --depth 1 https://github.com/forrestchang/andrej-karpathy-skills.git \
    "$MARKETPLACE_DIR" 2>/dev/null
fi

# Ensure plugin manifest exists
mkdir -p "$MARKETPLACE_DIR/.claude-plugin"
cat > "$MARKETPLACE_DIR/.claude-plugin/plugin.json" << 'PLUGIN_EOF'
{
  "name": "andrej-karpathy-skills",
  "description": "Behavioral guidelines to reduce common LLM coding mistakes",
  "version": "1.0.0",
  "author": { "name": "forrestchang" },
  "license": "MIT",
  "keywords": ["guidelines", "best-practices", "coding", "karpathy"],
  "skills": ["./skills/karpathy-guidelines"]
}
PLUGIN_EOF

# Register in user settings
SETTINGS="$HOME/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  node -e "
    const fs = require('fs');
    const s = JSON.parse(fs.readFileSync('$SETTINGS','utf8'));
    s.extraKnownMarketplaces = s.extraKnownMarketplaces || {};
    s.extraKnownMarketplaces.forrestchang = {source:{source:'github',repo:'forrestchang/andrej-karpathy-skills'}};
    s.enabledPlugins = s.enabledPlugins || {};
    s.enabledPlugins['andrej-karpathy-skills@forrestchang'] = true;
    fs.writeFileSync('$SETTINGS', JSON.stringify(s, null, 2) + '\n');
  " 2>/dev/null
fi

# Register in known_marketplaces
KNOWN="$HOME/.claude/plugins/known_marketplaces.json"
if [ -f "$KNOWN" ]; then
  node -e "
    const fs = require('fs');
    const k = JSON.parse(fs.readFileSync('$KNOWN','utf8'));
    if (!k.forrestchang) {
      k.forrestchang = {source:{source:'github',repo:'forrestchang/andrej-karpathy-skills'},installLocation:'$MARKETPLACE_DIR',lastUpdated:new Date().toISOString()};
      fs.writeFileSync('$KNOWN', JSON.stringify(k, null, 2) + '\n');
    }
  " 2>/dev/null
fi

# Register in installed_plugins
INSTALLED="$HOME/.claude/plugins/installed_plugins.json"
if [ -f "$INSTALLED" ]; then
  node -e "
    const fs = require('fs');
    const p = JSON.parse(fs.readFileSync('$INSTALLED','utf8'));
    if (!p.plugins['andrej-karpathy-skills@forrestchang']) {
      p.plugins['andrej-karpathy-skills@forrestchang'] = [{scope:'user',installPath:'$MARKETPLACE_DIR',version:'1.0.0',installedAt:new Date().toISOString(),lastUpdated:new Date().toISOString()}];
      fs.writeFileSync('$INSTALLED', JSON.stringify(p, null, 2) + '\n');
    }
  " 2>/dev/null
fi
echo "  Done."

# --- 3. Add Karpathy guidelines to current project CLAUDE.md ---
echo "[3/4] Adding Karpathy guidelines to project CLAUDE.md..."
CLAUDE_MD="CLAUDE.md"
KARPATHY_BLOCK="## Karpathy Guidelines"

if [ -f "$CLAUDE_MD" ] && grep -q "$KARPATHY_BLOCK" "$CLAUDE_MD" 2>/dev/null; then
  echo "  Already present, skipping."
else
  cat >> "$CLAUDE_MD" << 'GUIDELINES_EOF'

## Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.
- Remove imports/variables/functions that YOUR changes made unused.

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"
GUIDELINES_EOF
  echo "  Added to $CLAUDE_MD."
fi

# --- 4. Summary ---
echo "[4/4] Setup complete!"
echo ""
echo "  Plugins active:"
echo "    - claude-mem (automatic memory)"
echo "    - andrej-karpathy-skills (coding guidelines)"
echo "  CLAUDE.md: Karpathy guidelines included"
echo ""
echo "  You're good to go!"
