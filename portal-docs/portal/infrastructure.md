# Infrastructure

| Component | Detail |
|-----------|--------|
| Domain | icarus.eurekaendeavors.com |
| Server | Same host as GitLab Omnibus (18.9.1-ee) |
| GitLab | git.eurekaendeavors.com |
| Portal process | systemd service, Gunicorn on port 8000 |
| SSL | Caddy (Let's Encrypt, automatic) |

## Caddy Config
icarus.eurekaendeavors.com {
    reverse_proxy localhost:8000
}

## systemd Service
[Unit]
Description=Icarus Portal
After=network.target

[Service]
User=portal
WorkingDirectory=/opt/icarus-portal
EnvironmentFile=/opt/icarus-portal/.env
ExecStart=/opt/icarus-portal/venv/bin/gunicorn "portal:create_app()" --bind 127.0.0.1:8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

## Environment Variables (.env)
GITLAB_URL=https://git.eurekaendeavors.com
GITLAB_PAT=<personal access token>
SECRET_KEY=<flask secret key>
DATABASE_URL=sqlite:////opt/icarus-portal/portal.db

## GitLab Group: icarus
| ID | Project | Visibility | Purpose |
|----|---------|-----------|---------|
| 1 | icarus/pets | private | Pet editor Flask Blueprint |
| 2 | root/icarus-bug-reports | private | Bug report intake |
| 4 | icarus/prospects | private | Prospect editor Flask Blueprint |
| 5 | icarus/data-catalog | private | Data extraction scripts + JSON |
| 6 | icarus/portal | private | Portal (gateway) |
| 7 | icarus/core | private | Shared pip library (UE4 parser) |
