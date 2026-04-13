# Species Swap Research — Issue #18

## Species-Specific Fields

When swapping a creature's species, **6 fields** must be updated across 2 data locations, plus the talent array must be rebuilt.

### JSON-level fields (in `SavedMounts[]`)

| Field | Description |
|-------|-------------|
| `MountType` | Species identifier string (e.g., `Buffalo`, `Wolf`, `Wild_Boar`) |
| `MountIconName` | Numeric icon ID (e.g., `316749`) |

### Binary fields (in `RecorderBlob.BinaryData`)

| Field | Description |
|-------|-------------|
| `AISetupRowName` | AI behaviour row name (e.g., `Mount_Buffalo`) |
| `ActorClassName` | Blueprint class name (e.g., `BP_Mount_Buffalo_C`) |
| `ObjectFName` | Instance name = `ActorClassName` + `_` + `<numeric_id>` |
| `ActorPathName` | Full path = `<map_path>` + `.` + `ObjectFName` |

### Talent array (in `RecorderBlob.BinaryData`)

Talent row names contain species-specific suffixes that must be remapped to the new species tree.

## Complete Species Lookup Table

### Mounts (rideable + cargo)

| Type | ActorClassName | AISetupRowName | MountType (JSON) |
|------|---------------|----------------|------------------|
| ArcticMoa | `BP_Mount_Arctic_Moa_C` | `Mount_Arctic_Moa` | `Arctic_Moa`* |
| Blueback | `BP_Mount_Blueback_Daisy_C` | `Mount_Blueback_Daisy` | `Blueback`* |
| Buffalo | `BP_Mount_Buffalo_C` | `Mount_Buffalo` | `Buffalo` ✓ |
| Bull | `BP_Mount_Bull_C` | `Mount_Bull` | `Bull`* |
| Chew | `BP_Slinker_Mount_C` | `Mount_Slinker` | `Slinker`* |
| Horse | `BP_Mount_Horse_C` | `Mount_Horse` | `Horse`* |
| HorseStandard | `BP_Mount_Horse_Standard_C` | `Mount_Horse_Standard` | `Horse_Standard`* |
| Moa | `BP_Mount_Moa_C` | `Mount_Moa` | `Moa`* |
| SwampBird | `BP_Mount_SwampBird_C` | `Mount_SwampBird` | `SwampBird`* |
| SwampQuad | `BP_Swamp_Quadruped_Mount_C` | `Mount_SwampQuad` | `SwampQuad`* |
| Tusker | `BP_Mount_Tusker_C` | `Mount_Tusker` | `Tusker`* |
| WoollyMammoth | `BP_Mount_WoollyMammoth_C` | `Mount_WoollyMammoth` | `WoollyMammoth`* |
| WoolyZebra | `BP_Mount_Wooly_Zebra_C` | `Mount_Wooly_Zebra` | `Wooly_Zebra`* |
| Zebra | `BP_Mount_Zebra_C` | `Mount_Zebra` | `Zebra`* |

### Combat Pets (fight alongside player)

| Type | ActorClassName | AISetupRowName | MountType (JSON) |
|------|---------------|----------------|------------------|
| Boar | `BP_Tame_Boar_C` | `Tamed_Wild_Boar` | `Wild_Boar` ✓ |
| Cat | `BP_Tame_Cat_C` | `Mount_Cat` | `Cat`* |
| DesertWolf | `BP_Tamed_Wolf_Desert_C` | `Tamed_Desert_Wolf` | `Desert_Wolf`* |
| Dog | `BP_Tame_Dog_C` | `Mount_Dog`* | `Dog`* |
| SnowWolf | `BP_Tamed_Wolf_Snow_C` | `Tamed_Snow_Wolf` | `Snow_Wolf`* |
| TundraMonkey | `BP_Tundra_Monkey_C` | `Tamed_Tundra_Monkey` | `Tundra_Monkey`* |
| Wolf | `BP_Tamed_Wolf_C` | `Tamed_Forest_Wolf` | `Wolf` ✓ |

### Farm Animals (station-based production)

| Type | ActorClassName | AISetupRowName | MountType (JSON) |
|------|---------------|----------------|------------------|
| Chicken | `BP_Tame_Chicken_C` | `Mount_Chicken` | `Chicken`* |
| Cow | `BP_Tame_Cow_C` | `Mount_Cow`* | `Cow`* |
| Pig | `BP_Tame_Pig_C` | `Mount_Pig`* | `Pig`* |
| Rooster | `BP_Tame_Rooster_C` | `Mount_Rooster`* | `Rooster`* |
| Sheep | `BP_Tame_Sheep_C` | `Mount_Sheep` | `Sheep`* |

**Legend:** ✓ = confirmed from save data, * = derived from pak extraction patterns (needs verification)

## Naming Inconsistencies Found

| Issue | Example |
|-------|---------|
| Actor prefix varies | Mounts use `BP_Mount_`, pets use `BP_Tame_` or `BP_Tamed_` |
| Wolf is `Tamed` not `Tame` | `BP_Tamed_Wolf_C` (all wolf variants) vs `BP_Tame_Boar_C` |
| AISetup prefix varies | Mounts: `Mount_X`, wolf variants: `Tamed_X`, but Cat/Chicken/Sheep also use `Mount_` |
| Chew = Slinker internally | `BP_Slinker_Mount_C` and `Mount_Slinker` |
| Blueback has "Daisy" suffix | `BP_Mount_Blueback_Daisy_C` — variant name baked in |
| Boar has "Wild" qualifier | `Tamed_Wild_Boar` not `Tamed_Boar` |
| Wolf has "Forest" qualifier | `Tamed_Forest_Wolf` not `Tamed_Wolf` |
| Cat/Dog have sub-variants | `BP_Tame_Cat_A_C`/`B_C`/`C_C`, `BP_Tame_Dog_A_C`..`E_C` |

## Field Relationship Rules

```
ObjectFName   = {ActorClassName}_{numeric_instance_id}
ActorPathName = {map_path}.{ObjectFName}
```

During swap:
- **Preserve:** numeric instance ID, map path
- **Replace:** ActorClassName portion in ObjectFName and ActorPathName

## Talent Remapping Strategy

Talents follow naming patterns like:
- `Creature_Base_{Ability}_{Species}` (shared base talents)
- `Creature_{Species}_{Ability}` (species-specific talents)
- `CombatPet_{Ability}_{Species}` (combat pet talents)

**Approach:**
1. Get current mount's talent list with ranks
2. For each talent, extract the display name from `talent_data.TALENT_TREES`
3. Look up the equivalent talent in the new species tree (match by display name)
4. If found → preserve rank; if not found → refund (warn user)

## MountIconName Values

| Type | Icon ID | Source |
|------|---------|--------|
| Wild_Boar | `545995` | save data |
| Wolf | `386873` | save data |
| Buffalo | `316749` | save data |
| Others | **unknown** | need pak extraction or gameplay testing |

**Note:** These appear to be stable hash/ID values. A pak extraction for the icon mapping table would complete this.

## Implementation Priority

1. **Start with known types** (Boar, Wolf, Buffalo) — we have full data
2. **Add mount types** as data is confirmed from pak files
3. **Defer farm animals** until someone tests with farm saves
4. **Cat/Dog variants** — may need special handling for sub-variant selection
