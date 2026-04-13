# Icarus Save-file Toolkit

A desktop application for viewing and modifying your **Icarus** player save data, plus a powerful image extraction tool that rips every texture from the game. Built with Avalonia UI for cross-platform support.

The toolkit uses the `Icarus` core library (included in this repo) which handles all the parsing and serialization logic for the game's JSON save files.

---

## Table of Contents

- [Download](#download)
- [Save-file Toolkit (Desktop App)](#save-file-toolkit-desktop-app)
  - [Getting Started](#getting-started)
  - [Features](#features)
  - [Editing Workflow](#editing-workflow)
  - [Save File Locations](#save-file-locations)
- [Image Extractor (Python Tool)](#image-extractor-python-tool)
  - [Quick Start](#quick-start)
  - [Requirements](#requirements)
  - [Extraction Modes](#extraction-modes)
  - [Image Categories](#image-categories)
  - [Command Reference](#command-reference)
  - [Examples](#examples)
  - [How It Works](#how-it-works)
- [Building from Source](#building-from-source)
- [Project Structure](#project-structure)

---

## Download

Grab the latest **Icarus-Toolkit-Bundle.zip** from the [Releases](https://github.com/AgentKush/Icarus-Save-file-Toolkit/releases) page. It contains:

- **Icarus Toolkit.exe** -- The desktop save editor (no install needed, just run it)
- **extract_all_icons.py** -- The image extractor script (requires Python 3.8+)

---

## Save-file Toolkit (Desktop App)

### Getting Started

1. Download and extract `Icarus-Toolkit-Bundle.zip`
2. Run `Icarus Toolkit.exe`
3. The app auto-detects your Icarus save folder. If it can't find it, browse to:
   ```
   %LocalAppData%\Icarus\Saved\PlayerData\<YourSteamID>
   ```
4. Select a character from the dropdown
5. Toggle **Edit Mode** to unlock editing
6. Make your changes across the tabs
7. Click **Save All Data** to write back to your save files

> **Always create a backup first.** Use the Backup button before making any changes. The app creates timestamped backups you can restore from at any time.

### Features

**Character Management**

- Edit character name, XP, and level
- Duplicate characters (great for experimenting)
- Remove characters you no longer need
- Edit character status fields: IsDead, IsAbandoned, Location, Prospect ID

**Profile & Currency**

- Edit Ren (standard currency) and Exotic currency amounts
- View your User ID and Data Version
- All profile-level data accessible in one place

**Talent Editor**

- View all character talents with their RowName and Rank
- Add new talents by name
- Remove talents you don't want
- Edit talent ranks (upgrade or reset)
- Separate view for profile-level talents vs character talents

**Cosmetics Editor**

Full control over character appearance:

- Head, Hair, Hair Color
- Body, Body Color, Skin Tone
- Head Tattoo, Head Scar
- Facial Hair, Cap Logo
- Voice, Eye Color, Gender

**Meta Inventory & Loadouts**

- View and edit workshop items in your meta inventory
- Manage loadouts and their assigned equipment slots
- Add or remove items from loadout configurations

**Mounts**

- View all unlocked mounts and their data
- Edit mount properties

**Bestiary & Accolades**

- Browse bestiary entries (creature discovery data)
- View accolade progress and completion status

**Flags / Tech Tree**

- View all unlocked flag IDs (tech tree nodes, story flags, etc.)
- Add flag IDs to unlock specific tech or content
- Remove flags to re-lock content
- Flags are named and categorized for easy browsing

**Backup & Restore**

- Create timestamped backups of all game data with one click
- Browse a list of all available backups with dates
- Restore any backup instantly -- rolls back Characters, Profile, and all related files

### Editing Workflow

The app operates in two modes:

1. **View Mode** (default) -- All fields are read-only. Browse your save data safely without risk of accidental changes.
2. **Edit Mode** -- Toggle the Edit Mode switch to unlock all editable fields. Fields turn editable and the Save button becomes active.

Changes are only written when you explicitly click **Save All Data**. If you close the app or switch characters without saving, your changes are discarded.

### Save File Locations

Icarus stores save data at:

```
%LocalAppData%\Icarus\Saved\PlayerData\<SteamID64>\
```

Inside that folder you'll find:

| File | Contents |
|------|----------|
| `Characters.json` | All character data (stats, talents, cosmetics, inventory) |
| `Profile.json` | Profile-level data (currencies, profile talents, unlocks) |
| `MetaInventory.json` | Workshop items and meta inventory |
| `Loadouts.json` | Saved loadout configurations |
| `Mounts.json` | Mount unlock and customization data |
| `Bestiary.json` | Creature discovery tracking |
| `Accolades.json` | Achievement/accolade progress |

The toolkit reads and writes all of these files.

---

## Image Extractor (Python Tool)

A standalone Python script that extracts every texture from Icarus as PNG files -- item icons, loading screens, HUD elements, creature textures, environment art, and more. No external tools required beyond Python and Pillow.

### Quick Start

```bash
# Extract all UI icons (default, auto-detects game location)
python extract_all_icons.py

# Extract EVERYTHING in the game
python extract_all_icons.py --all

# Extract just loading screens
python extract_all_icons.py --loading-screens
```

### Requirements

- **Python 3.8+** (any recent Python works)
- **Pillow** (auto-installed if missing -- you don't need to do anything)
- **FModel exports** of Icarus game files (the script tells you how to set this up if it can't find them)

The script auto-detects your Steam library and Icarus install location. If auto-detection fails, point it manually:

```bash
python extract_all_icons.py --base "D:\Games\Icarus\Exports\Icarus\Content"
```

### Extraction Modes

The extractor supports two source modes:

**FModel Exports (default)** -- Reads from FModel-exported `.uexp` + `.json` + `.ubulk` files. This is the recommended mode and produces the highest quality results. You need to export the game files using [FModel](https://fmodel.app/) first.

**Direct PAK Extraction** -- Reads directly from the game's `.pak` files with no FModel needed. Use the `--game` flag:

```bash
python extract_all_icons.py --game --all
```

This mode handles PAK v7-v11, zlib decompression, and Oodle DLL loading automatically. Useful if you don't want to install FModel, though FModel exports tend to give better results for complex textures.

### Image Categories

The extractor organizes images into 10 categories. By default only UI icons are extracted. Use flags to select what you want:

| Flag | Category | What's Included |
|------|----------|-----------------|
| `--icons` | UI Icons | Item icons, achievement icons, talent icons, HUD elements, status icons |
| `--loading-screens` | Loading Screens | Biome splash art, mission loading screens |
| `--backgrounds` | Backgrounds | Menu backgrounds, title screen art |
| `--cinematics` | Cinematics | Cutscene frames, story art sequences |
| `--marketing` | Marketing | Promotional art, store images |
| `--environment` | Environment | Biome textures, terrain art, skyboxes |
| `--creatures` | Creatures | Animal and creature textures, skins |
| `--vfx` | VFX | Particle textures, effect sprites |
| `--materials` | Materials | Surface textures, material maps |
| `--misc-art` | Misc Art | Concept art, renders, other 2D art |
| `--all` | Everything | All of the above combined |

### Command Reference

**Source options:**

| Flag | Description |
|------|-------------|
| `--base PATH` | Path to FModel exports Content folder (auto-detected if omitted) |
| `--game` | Extract directly from game PAK files instead of FModel exports |
| `--paks PATH` | Path to Icarus Paks directory (auto-detected if omitted) |

**Output options:**

| Flag | Description |
|------|-------------|
| `--out PATH` | Output directory for PNGs (default: `Desktop/icarus_icons`) |
| `--filter KEYWORD` | Only extract images matching this keyword (e.g. `"Lithium"`) |
| `--dry-run` | List what would be extracted without actually extracting |
| `--force` | Re-extract and overwrite existing PNGs |
| `--organize` | Sort output into subdirectories by category (on by default) |

### Examples

```bash
# Extract only icons that match "Rifle" in the name
python extract_all_icons.py --filter "Rifle"

# Extract loading screens and backgrounds to a custom folder
python extract_all_icons.py --loading-screens --backgrounds --out "C:\MyArt"

# See what would be extracted without doing it
python extract_all_icons.py --all --dry-run

# Force re-extract everything (overwrite existing)
python extract_all_icons.py --all --force

# Direct PAK extraction (no FModel needed)
python extract_all_icons.py --game --icons

# Extract creature textures with a keyword filter
python extract_all_icons.py --creatures --filter "Bear"
```

### How It Works

The extractor handles the full UE4 texture pipeline:

1. **Asset Discovery** -- Scans FModel exports (or unpacked PAK files) for `.uexp` texture files. Uses a quick binary scan to identify which `.uexp` files contain texture data by looking for pixel format strings (`PF_DXT1`, `PF_DXT5`, `PF_BC7`, etc.).

2. **Metadata Extraction** -- Reads texture dimensions, pixel format, and mip chain info from either the FModel `.json` sidecar or by parsing the `.uexp` binary directly (heuristic FString scanning for the pixel format, then reading width/height/mip count from surrounding bytes).

3. **Bulk Data Reading** -- Handles UE4's split storage: small textures store pixel data inline in `.uexp`, but larger textures store their full-resolution mip0 in a separate `.ubulk` file. The extractor reads from both.

4. **DDS Assembly** -- Builds a DDS file in memory with the correct header for the pixel format. Supports standard DDS headers for DXT1/DXT5/B8G8R8A8 and DX10 extended headers for BC4/BC5/BC7/FloatRGBA and other modern formats.

5. **PNG Conversion** -- Uses Pillow to decode the DDS data and save as PNG. Includes custom decoders for formats Pillow doesn't handle natively: PF_G8 (grayscale), PF_A8 (alpha-only), and PF_FloatRGBA (16-bit half-float HDR).

**Supported pixel formats:** PF_DXT1, PF_DXT5, PF_BC7, PF_B8G8R8A8, PF_BC1, PF_BC3, PF_BC4, PF_BC5, PF_BC6H, PF_G8, PF_A8, PF_FloatRGBA, PF_R8G8, PF_R8, PF_R16F, PF_R32F, PF_G16R16, PF_G16R16F, PF_A16B16G16R16, PF_ASTC_4x4, PF_ETC2_RGB, PF_ETC2_RGBA, and more.

---

## Building from Source

The desktop app is a .NET 8 / Avalonia project. To build:

```bash
# Restore dependencies
dotnet restore

# Build (debug)
dotnet build

# Publish a single-file executable for Windows
dotnet publish "Icarus Toolkit/Icarus Toolkit.csproj" -c Release -r win-x64 --self-contained
```

The published executable lands in `Icarus Toolkit/bin/Release/net8.0/win-x64/publish/`.

### Tech Stack

- **.NET 8** (upgraded from .NET Framework 4.8 / .NET 6)
- **Avalonia 11.2** (upgraded from 0.10.18)
- **CommunityToolkit.Mvvm 8.4** for MVVM pattern
- **Serilog** for structured logging
- **System.Text.Json** for save file parsing

---

## Project Structure

```
Icarus Save-file Toolkit/
|
|-- Icarus/                         # Core library - save file parsing & serialization
|   |-- Core.cs                     # XP/level calculation tables
|   |-- GameData.cs                 # Save file path management, backup/restore
|   |-- CharacterExplorer.cs        # Character data read/write
|   |-- ProfileExplorer.cs          # Profile data (currencies, talents)
|   |-- MetaInventoryExplorer.cs    # Workshop item inventory
|   |-- LoadoutsExplorer.cs         # Loadout configurations
|   |-- MountsExplorer.cs           # Mount data
|   |-- BestiaryExplorer.cs         # Creature bestiary
|   |-- AccoladeData.cs             # Accolade definitions & progress
|   |-- AccoladesExplorer.cs        # Accolade data read/write
|   |-- FlagDefinitions.cs          # Named flag ID mappings
|   |-- WorkshopItemData.cs         # Workshop item definitions
|   '-- ExtensionMethods.cs         # Deep clone via JSON serialization
|
|-- Icarus Toolkit/                 # Desktop UI application (Avalonia)
|   |-- ViewModels/
|   |   '-- MainWindowViewModel.cs  # All app logic, commands, and state
|   |-- Views/
|   |   '-- MainWindow.axaml        # Full UI layout (tabs, editors, etc.)
|   '-- Utils/
|       |-- IconResolver.cs         # Game icon loading for the UI
|       |-- SettingsManager.cs      # Persistent app settings
|       '-- InverseBooleanConverter.cs
|
|-- tools/
|   '-- extract_all_icons.py        # Image Extractor v7 (standalone Python script)
|
|-- icarus_icons/                   # Pre-extracted icon library (134 categories)
|
'-- Icarus-Toolkit-Bundle.zip       # Distribution bundle (exe + extractor script)
```

---

## Credits

Forked from [asm512/Icarus-Toolkit](https://github.com/asm512/Icarus-Toolkit) and significantly extended with new editors, image extraction, and .NET 8 / Avalonia 11 upgrades.

## License

See the original repository for license information.
