# Icarus Save-file Toolkit

A desktop application for viewing and modifying your Icarus player save data. Built with Avalonia UI for cross-platform support.

It uses the `Icarus` core library (included in this repo) which handles all the parsing and serialization logic for the game's JSON save files.

## Features

- **Character Management**
  - [x] Read & write character data
  - [x] Edit character name, XP, and level
  - [x] Duplicate characters
  - [x] Remove characters
  - [x] Edit character status (IsDead, IsAbandoned, Location, Prospect ID)

- **Profile & Currency**
  - [x] Read & write profile data
  - [x] Edit Ren and Exotic currency amounts
  - [x] View User ID and Data Version

- **Talent Editor**
  - [x] View all character talents (RowName & Rank)
  - [x] Add and remove talents
  - [x] Edit talent ranks
  - [x] View profile-level talents

- **Cosmetics Editor**
  - [x] View and edit all character cosmetic values
  - [x] Head, Hair, Hair Color, Body, Body Color, Skin Tone
  - [x] Head Tattoo, Head Scar, Facial Hair, Cap Logo
  - [x] Voice, Eye Color, Gender

- **Flags / Tech Tree**
  - [x] View all unlocked flags
  - [x] Add and remove flag IDs

- **Backup & Restore**
  - [x] Create timestamped backups of all game data
  - [x] List available backups
  - [x] Restore from any backup

## Tech Stack

- **.NET 8** (upgraded from .NET Framework 4.8 / .NET 6)
- **Avalonia 11.2** (upgraded from 0.10.18)
- **CommunityToolkit.Mvvm 8.4** for MVVM pattern
- **Serilog** for logging
- **System.Text.Json** for save file parsing

## Building

```bash
dotnet restore
dotnet build
```

To publish a single-file executable:
```bash
dotnet publish "Icarus Toolkit/Icarus Toolkit.csproj" -c Release -r win-x64 --self-contained
```

## Project Structure

```
Icarus/                    # Core library - data parsing & serialization
  Core.cs                  # XP/level calculation
  GameData.cs              # Save file path management, backup/restore
  CharacterExplorer.cs     # Character data read/write, models
  ProfileExplorer.cs       # Profile data read/write, models
  ExtensionMethods.cs      # Deep clone via JSON serialization

Icarus Toolkit/            # Desktop UI application (Avalonia)
  ViewModels/              # MVVM ViewModels
  Views/                   # XAML views
  Utils/                   # Settings manager, converters
  Assets/                  # Icons and images
```

## Usage

1. Launch the application
2. Select your Icarus game data folder (typically `%LocalAppData%\Icarus\Saved\PlayerData\<SteamID>`)
3. Select a character from the dropdown
4. Toggle **Edit Mode** to make changes
5. Use the tabs to edit Overview, Talents, Cosmetics, Flags, or Profile data
6. Click **Save All Data** to write changes back to your save files

> **Tip:** Always create a backup before editing. Use the Backup button before making changes.
