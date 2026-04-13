# Deployment Guide

Architecture: Internet -> Caddy (TLS) -> Gunicorn 0.0.0.0:5000 -> Flask App -> SQLite

## Quick Install
git clone https://git.eurekaendeavors.com/root/icarus-prospects.git /tmp/icarus-install
sudo bash /tmp/icarus-install/deploy/install.sh

## Environment Variables
FLASK_ENV=prod
SECRET_KEY=<random>
DATABASE_URL=sqlite:////opt/icarus-prospects/webapp/instance/icarus.db
MAX_UPLOAD_MB=50
SESSION_TTL=3600

## Project Structure
webapp/app.py - App factory, routes, session management
webapp/models.py - SQLAlchemy models (EditSession, Blob, UsageEvent)
webapp/services/mission_service.py - Mission parsing, cascading, reset
webapp/data/gh_chains.json - Great Hunt chain definitions
webapp/data/mission_metadata.json - Mission display names
core/ue4_parser.py - UE4 binary parser
core/ue4_serializer.py - Byte-perfect serializer
core/save_io.py - Save file I/O helpers
