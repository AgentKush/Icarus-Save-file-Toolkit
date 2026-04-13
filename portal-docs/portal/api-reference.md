# API Reference

Base URL: https://git.eurekaendeavors.com/api/v4/

## Project Data
| Purpose | Method | Endpoint |
|---------|--------|----------|
| Project details | GET | /projects/:id |
| README content | GET | /projects/:id/repository/files/README.md/raw?ref=main |
| Releases list | GET | /projects/:id/releases |
| Wiki page list | GET | /projects/:id/wikis |
| Wiki page content | GET | /projects/:id/wikis/:slug |
| Source archive (zip) | GET | /projects/:id/repository/archive.zip?sha=:ref |

## Git Smart HTTP (Proxied)
| Purpose | Method | Path |
|---------|--------|------|
| Ref discovery | GET | /:namespace/:repo.git/info/refs?service=git-upload-pack |
| Pack transfer | POST | /:namespace/:repo.git/git-upload-pack |

## Project IDs
| ID | Project | Slug | Exposed |
|----|---------|------|---------|
| 1 | icarus/pets | pets | Yes |
| 2 | root/icarus-bug-reports | (none) | No |
| 4 | icarus/prospects | prospects | Yes |
| 5 | icarus/data-catalog | data-catalog | Yes |
| 6 | icarus/portal | (none) | No |
| 7 | icarus/core | (none) | No |
