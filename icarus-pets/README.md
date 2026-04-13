# icarus-pets

Data library and generation scripts for Icarus mount, pet, and farm animal data. Used as a submodule by the [Eureka Portal](https://git.eurekaendeavors.com/icarus/eureka-portal).

> **Looking for the desktop editor?** The standalone Tkinter GUI has been archived to [icarus-pets-tkinter-deprecated](https://git.eurekaendeavors.com/icarus/icarus-pets-tkinter-deprecated).

## Contents

- **`talent_data.py`** — Auto-generated talent trees for all 26+ creature types (656 talents across 34 trees), genetics, lineage data, species detection, and swap logic
- **`variation_data.py`** — Phenotype/appearance variation mappings per creature type
- **`bestiary_data.json`** — Bestiary lore and creature metadata
- **`ue4_parser.py`** / **`ue4_serializer.py`** — UE4 binary property parser and serializer for Icarus save files
- **`pak_talents_extracted.json`** / **`pak_variations_extracted.json`** — Raw extracted data from game pak files
- **`assets/icons/`** — WebP talent icons (128px) extracted from game files, with `talent_icon_map.json` lookup
- **`scripts/`** — Data generation and refresh scripts

## Usage as Submodule

```bash
# In the portal project
git submodule add https://git.eurekaendeavors.com/icarus/pets.git icarus-pets
git submodule update --init
```

## Refreshing Data

When a new Icarus game update drops:

```bash
# Re-extract talent and variation data from pak files
python scripts/refresh_talent_data.py

# Verify the refresh
python scripts/verify_refresh.py

# Run tests
python -m pytest tests/ -v
```

## Tests

```bash
python -m pytest tests/ -v
```

## License

See [LICENSE](LICENSE).
