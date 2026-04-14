#!/bin/bash
# Session Start Hook: Re-install plugins for Claude Code web sessions
# This runs automatically when a new session begins

# Install claude-mem plugin
npx -y claude-mem install 2>/dev/null

# Install andrej-karpathy-skills plugin
if [ ! -d "$HOME/.claude/plugins/marketplaces/forrestchang" ]; then
  git clone https://github.com/forrestchang/andrej-karpathy-skills.git \
    "$HOME/.claude/plugins/marketplaces/forrestchang" 2>/dev/null

  # Create plugin manifest if not present
  mkdir -p "$HOME/.claude/plugins/marketplaces/forrestchang/.claude-plugin"
  cat > "$HOME/.claude/plugins/marketplaces/forrestchang/.claude-plugin/plugin.json" << 'PLUGIN_EOF'
{
  "name": "andrej-karpathy-skills",
  "description": "Behavioral guidelines to reduce common LLM coding mistakes, derived from Andrej Karpathy's observations on LLM coding pitfalls",
  "version": "1.0.0",
  "author": { "name": "forrestchang" },
  "license": "MIT",
  "keywords": ["guidelines", "best-practices", "coding", "karpathy"],
  "skills": ["./skills/karpathy-guidelines"]
}
PLUGIN_EOF
fi

# Register marketplace and enable plugin in settings if not already present
SETTINGS="$HOME/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  if ! grep -q "forrestchang" "$SETTINGS" 2>/dev/null; then
    # Add forrestchang marketplace and plugin via node
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
fi

# Update known_marketplaces.json
KNOWN="$HOME/.claude/plugins/known_marketplaces.json"
if [ -f "$KNOWN" ] && ! grep -q "forrestchang" "$KNOWN" 2>/dev/null; then
  node -e "
    const fs = require('fs');
    const k = JSON.parse(fs.readFileSync('$KNOWN','utf8'));
    k.forrestchang = {source:{source:'github',repo:'forrestchang/andrej-karpathy-skills'},installLocation:'$HOME/.claude/plugins/marketplaces/forrestchang',lastUpdated:new Date().toISOString()};
    fs.writeFileSync('$KNOWN', JSON.stringify(k, null, 2) + '\n');
  " 2>/dev/null
fi

# Update installed_plugins.json
INSTALLED="$HOME/.claude/plugins/installed_plugins.json"
if [ -f "$INSTALLED" ] && ! grep -q "andrej-karpathy-skills" "$INSTALLED" 2>/dev/null; then
  node -e "
    const fs = require('fs');
    const p = JSON.parse(fs.readFileSync('$INSTALLED','utf8'));
    p.plugins['andrej-karpathy-skills@forrestchang'] = [{scope:'user',installPath:'$HOME/.claude/plugins/marketplaces/forrestchang',version:'1.0.0',installedAt:new Date().toISOString(),lastUpdated:new Date().toISOString()}];
    fs.writeFileSync('$INSTALLED', JSON.stringify(p, null, 2) + '\n');
  " 2>/dev/null
fi
