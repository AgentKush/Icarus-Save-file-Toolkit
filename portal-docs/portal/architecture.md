# Portal Architecture

## Overview
Portal sits between public internet and GitLab. Every user-facing request handled by portal.

## Stack
- Caddy (SSL termination) -> Flask portal (Gunicorn, localhost:8000) -> GitLab API (PAT auth, server-side only)
- GitLab repos are private. PAT stored in .env.

## Application Structure
```
icarus/portal
├── portal/
│   ├── __init__.py           # App factory (create_app), landing route at /
│   ├── config.py             # Dev/Test/Prod configuration
│   ├── extensions.py         # Shared Flask extensions (SQLAlchemy)
│   ├── templates/
│   │   ├── base.html         # Shared portal base (nav, landmarks, a11y)
│   │   └── index.html        # Landing page (tool cards)
│   ├── static/
│   │   ├── css/app.css       # Shared styles + WCAG AA palette
│   │   └── js/app.js         # Shared JS (announce, disclaimer modal)
│   └── blueprints/
│       ├── prospects/        # Prospect save editor
│       │   ├── __init__.py   # Blueprint factory
│       │   ├── models.py     # SQLAlchemy models
│       │   ├── routes.py     # Upload, editor, API routes
│       │   ├── services/     # Mission parsing, cascade, reset logic
│       │   ├── data/         # Game data (gh_chains.json, metadata)
│       │   ├── templates/    # Jinja2 templates
│       │   └── static/       # CSS + JS
│       ├── pets/             # Pet editor
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── routes.py
│       │   ├── services/     # Mount parsing, talents, genetics, species swap
│       │   ├── data/         # Bestiary, talent, variation data
│       │   ├── templates/
│       │   └── static/
│       └── catalog/          # Data catalog
├── tests/                    # Pytest test suite
├── deploy/                   # Caddy config, systemd unit
├── scripts/                  # GitLab admin scripts
└── wiki/                     # Wiki (separate git repo)

icarus/core                   # pip install -e ../icarus-core
├── icarus_core/
│   ├── ue4_parser.py         # BinaryReader/Writer + property parser
│   ├── ue4_serializer.py     # Property tree → binary serialization
│   └── save_io.py            # JSON I/O, blob compress/decompress, actor helpers
└── pyproject.toml

icarus/data-catalog           # extraction scripts, not a pip package
```

## Slug-to-Project Mapping
| Slug | GitLab Project | ID | Purpose |
|------|---------------|-----|---------|
| pets | icarus/pets | 1 | Pet editor |
| prospects | icarus/prospects | 4 | Prospect editor |
| data-catalog | icarus/data-catalog | 5 | Data catalog |

## Data Flows
### Pet editor: Request /pets -> Blueprint handles -> Parse/serialize via icarus/core -> Modified file back
### Prospect editor: Upload -> Validate JSON -> Extract ProspectBlob -> Decompress + parse UE4 binary -> SQLite session -> Editor page -> AJAX toggle with cascading -> Apply resets -> Download
### Git clone: git clone portal URL -> Proxy info/refs to GitLab -> Proxy git-upload-pack -> Client receives packfile
