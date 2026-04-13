## Icarus Save-file Toolkit v1.0.0

First official release bundling the desktop save editor and image extractor together.

---

### Save Editor (Desktop App)

Full-featured save editor for Icarus with tabbed UI:

- **Character Management** - Edit name, XP, level, status (IsDead, IsAbandoned, Location, Prospect ID). Duplicate and remove characters.
- **Profile & Currency** - Edit Ren and Exotic currency amounts. View User ID and Data Version.
- **Talent Editor** - View, add, remove, and edit talent ranks for both character and profile talents.
- **Cosmetics Editor** - Full appearance customization: head, hair, body, skin tone, tattoos, scars, facial hair, cap logo, voice, eye color, gender.
- **Meta Inventory** - View and edit workshop items in meta inventory.
- **Loadouts** - Manage loadout configurations and equipment slots.
- **Mounts** - View and edit mount data and unlocks.
- **Bestiary & Accolades** - Browse creature discovery data and accolade progress.
- **Flags / Tech Tree** - View, add, and remove unlocked flag IDs with named categories.
- **Backup & Restore** - One-click timestamped backups with instant restore.
- **Icon Display** - Shows actual game icons for items, achievements, and talents in the UI (7,298 icons across 134 categories).

### Image Extractor v7

Standalone Python tool that extracts every texture from Icarus as PNG:

- **7,000+ textures** extractable across 10 categories
- **10 image categories**: UI Icons, Loading Screens, Backgrounds, Cinematics, Marketing Art, Environment Textures, Creature Textures, VFX/Particles, Material Textures, Concept/Misc Art
- **.ubulk companion file support** for large textures (BuildGuide, WeatherTier, Flaticons, title screens, scope textures, etc.)
- **DX10 extended DDS headers** for BC4, BC5, BC7, FloatRGBA, and other modern formats
- **Custom decoders** for PF_G8 (grayscale), PF_A8 (alpha-only), PF_FloatRGBA (16-bit HDR)
- **Direct PAK extraction** mode - extract from game .pak files without needing FModel
- **Auto-detection** of Steam library and Icarus install location
- **Category filtering** - extract only what you need with `--icons`, `--loading-screens`, `--backgrounds`, etc.
- **Keyword filtering** - `--filter "Rifle"` to extract only matching textures
- **Smart skip** - only extracts new/changed textures unless `--force` is used

---

### Changelog (All Updates)

**Image Extractor v7** - .ubulk Support
- Added `.ubulk` companion file reading for textures with external mip storage
- Extracted 69 new textures previously showing "no texture data found" (BuildGuide series, WeatherTier icons, Flaticons, Hook icons, title screen backgrounds, scope textures)
- Added safety cap (256MB) on single mip reads
- Improved error handling with narrower exception catches
- Added diagnostic tool (`debug_ubulk.py`) for troubleshooting extraction failures

**Image Extractor v6** - Full Category Expansion
- Expanded from 1 category (UI icons) to 10 image categories
- Added 1,219 lines of new extraction code
- Added PF_G8 grayscale decoder
- Added PF_A8 alpha-only decoder
- Added PF_FloatRGBA 16-bit half-float HDR decoder
- Added DX10 extended DDS header support (DXGI format mapping)
- Added direct PAK file extraction (v7-v11, zlib, Oodle)
- Added heuristic binary parser for textures without JSON metadata
- Added multi-chunk texture scanner for better file detection
- Fixed argparse key mismatches (loading_screens vs loading-screens)

**Accolades & Bundle**
- Added AccoladeData.cs with full accolade definitions
- Added AccoladesExplorer.cs for reading/writing accolade data
- Created Icarus-Toolkit-Bundle.zip distribution format
- Initial extract_all_icons.py (833 lines, UI icons only)

**Icon System**
- Built IconResolver utility for displaying game icons in the UI
- Added icon_manifest.txt with 7,298 icon paths across 134 categories
- Extracted 100+ achievement icons as PNGs

**Major Cleanup**
- Removed embedded icarus-pets subproject (19,555 lines removed)
- Removed portal-docs directory
- Cleaned up .gitignore
- Streamlined repository to focus on the toolkit

**Big Update - Meta Inventory, Loadouts, Mounts**
- Added MetaInventoryExplorer for workshop item management
- Added LoadoutsExplorer for loadout configuration
- Added MountsExplorer for mount data
- Added BestiaryExplorer for creature discovery
- Added WorkshopItemData definitions
- Extended MainWindowViewModel with new editor tabs

**Core Save Editing**
- Character data read/write with full field editing
- Profile data with Ren, Exotics, and XP editing
- Talent system with add/remove/rank editing
- Cosmetics editor with all appearance values
- Flag/tech tree management with named definitions
- Character duplication and removal
- Backup and restore system with timestamped snapshots
- Game data path auto-detection and manual selection
- Logging via Serilog

**Platform Upgrade**
- Upgraded from .NET Framework 4.8 to .NET 8
- Upgraded from Avalonia 0.10.18 to Avalonia 11.2
- Upgraded to CommunityToolkit.Mvvm 8.4
- Single-file executable publishing

---

### Download

Extract `Icarus-Toolkit-Bundle.zip` and you get:
- **Icarus Toolkit.exe** - Run this for the save editor (no install needed)
- **extract_all_icons.py** - Run with Python 3.8+ for image extraction
