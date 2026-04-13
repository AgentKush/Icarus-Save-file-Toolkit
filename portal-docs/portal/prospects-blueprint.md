# Prospects Blueprint

## Blueprint Structure
portal/blueprints/prospects/
├── __init__.py              Blueprint factory
├── models.py                SQLAlchemy models: ProspectEditSession, SiteVisit, UsageEvent
├── routes.py                HTTP routes:
│                              GET  /              Upload page
│                              POST /upload         File upload + parse
│                              GET  /editor         Mission editor UI
│                              POST /api/toggle     AJAX mission toggle
│                              POST /api/apply      Generate modified save
│                              GET  /api/download   Download modified save
│                              GET  /api/state      Current session state
├── services/
│   └── mission_service.py   Core logic: parse_save_json(), extract_missions(),
│                            apply_dependency_cascade(), apply_resets(), etc.
├── data/
│   ├── gh_chains.json       GH mission chain definitions
│   ├── mission_metadata.json  Display names + descriptions
│   └── data_version.json    Data version tracking
├── templates/prospects/
│   ├── base.html            Dark Bootstrap 5 base layout
│   ├── upload.html          File upload form
│   ├── editor.html          Interactive mission editor
│   └── error.html           Error display page
└── static/
    ├── css/app.css          Custom styles
    └── js/editor.js         AJAX toggle/apply/download, ARIA announcements

## Dependency Cascading
### Great Hunts: Uncheck cascades downstream, Check cascades upstream
### Expedition→Biome: Uncheck expedition unchecks all biome missions
### Story Chains (PRO/ELY): Sequential dependencies

## Session Management
- Each upload creates ProspectEditSession in SQLite
- Session ID in Flask session cookie
- Sessions expire after TTL (default 1 hour)
- Expired sessions cleaned by before_request hook

## API Toggle Request/Response
POST /prospects/api/toggle
Request: {"mission_name": "GH_RG_B", "completed": false, "mission_index": null}
Response: {"affected": [...], "pending_count": 2, "pending_missions": [...]}

POST /prospects/api/apply
Response: {"removed_missions": [...], "verification": {"passed": true}, "duration_ms": 42}
