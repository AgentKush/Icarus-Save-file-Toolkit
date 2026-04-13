"""Check release package info via GitLab Package Registry.

Note: GitLab's Generic Package Registry does not track download counts.
Only last_downloaded_at is available via the API. For actual download
counts, parse the nginx access logs on the GitLab server:

  grep 'packages/generic/icarus-pet-editor' /var/log/gitlab/nginx/gitlab_access.log \\
    | grep ' 200 ' | awk '{print $7}' | grep -oP 'v[0-9.]+' | sort | uniq -c

Usage: python scripts/check_downloads.py
"""
import urllib.request, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', '.gitlab_token')
API_BASE = 'https://git.eurekaendeavors.com/api/v4/projects/1'

def get_token():
    with open(TOKEN_FILE) as f:
        return f.read().strip()

def api_get(path, token):
    req = urllib.request.Request(f'{API_BASE}{path}')
    req.add_header('PRIVATE-TOKEN', token)
    return json.loads(urllib.request.urlopen(req).read())

def main():
    token = get_token()

    try:
        packages = api_get('/packages?package_type=generic&package_name=icarus-pet-editor&per_page=50', token)
    except urllib.error.HTTPError:
        print("No packages found in Package Registry.")
        return

    if not packages:
        print("No packages found.")
        return

    print("Package Registry — Release History:")
    print("=" * 55)
    for pkg in sorted(packages, key=lambda p: p['version']):
        last_dl = pkg.get('last_downloaded_at') or 'never'
        print(f"  v{pkg['version']}")
        print(f"    created:         {pkg['created_at']}")
        print(f"    last downloaded: {last_dl}")
        files = api_get(f'/packages/{pkg["id"]}/package_files', token)
        for f in files:
            size_mb = f['size'] / 1_048_576
            print(f"    file:            {f['file_name']} ({size_mb:.1f} MB)")
    print("=" * 55)
    print("NOTE: Download counts are not available via the GitLab API")
    print("      for Generic Package Registry entries. Check nginx logs")
    print("      on the server for actual download counts.")

if __name__ == '__main__':
    main()
