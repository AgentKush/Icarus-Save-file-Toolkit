# Tech Stack

| Component | Choice | Notes |
|-----------|--------|-------|
| Framework | Flask (Python) | WSGI; Blueprint-based multi-tool structure |
| Templating | Jinja2 | Server-rendered HTML; no client-side framework |
| Database | SQLite via SQLAlchemy | Download tracking, clone metrics |
| HTTP client | httpx | Sync HTTP client for GitLab API calls and streaming |
| WSGI server | Gunicorn | Production WSGI server |
| Reverse proxy | Caddy | SSL via Let's Encrypt |
| Analytics | Umami | Self-hosted, privacy-respecting |
| Deployment | systemd service | Gunicorn on port 8000 behind Caddy |
| License | GPL v3 | |

## Python Dependencies
flask>=3.0.0
gunicorn>=21.0.0
jinja2>=3.1.3
sqlalchemy>=2.0.0
httpx>=0.27.0
python-multipart>=0.0.9

## Shared core library (UE4 parser/serializer)
Both icarus-pets (desktop) and the prospects Blueprint depend on same UE4 binary parsing logic.
Extracted into core/ within portal repo:
- core/ue4_parser.py
- core/ue4_serializer.py
- core/save_io.py
