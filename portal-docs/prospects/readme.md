# Icarus Prospects Save Editor

## Features
- Parse 34MB+ UE4 binary blobs in under a second
- Great Hunts with dependency cascading
- Open World missions grouped by biome
- Binary reset: removes mission history, session flags, quest actors, quest manager state
- Verification: re-parse, actor count check, zero trailing bytes
- Game-tested: modified saves load correctly

## Supported Maps
| Map | Prefix | Great Hunts |
|-----|--------|-------------|
| Olympus | OLY_ | Rock Golem (GH_RG_*) |
| Styx | STYX_ | Great Ape (GH_Ape_*) |
| Prometheus | PRO_ | Ice Mammoth (GH_IM_*) |

## Database: SQLite
- EditSession: UUID sessions with TTL, status, mission state
- Blob: Original and modified compressed binary blobs
- UsageEvent: All actions tracked with timestamps
