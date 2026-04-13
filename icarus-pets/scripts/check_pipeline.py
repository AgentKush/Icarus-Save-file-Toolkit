"""Check CI/CD pipeline status for the latest tag."""
import json
import urllib.request

GITLAB_URL = "https://git.eurekaendeavors.com"
PROJECT_ID = 1

with open('.gitlab_token') as f:
    TOKEN = f.read().strip()


def api_get(path):
    """GET from GitLab API."""
    url = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}{path}"
    req = urllib.request.Request(url)
    req.add_header('PRIVATE-TOKEN', TOKEN)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main():
    print("=== CI/CD Pipeline Status ===\n")

    pipelines = api_get("/pipelines?per_page=5")
    for p in pipelines:
        marker = " ◀" if "v2.1.1" in p["ref"] else ""
        print(f"  Pipeline #{p['id']} ({p['ref']}): {p['status']}{marker}")

    # Get jobs for the v2.1.1 pipeline
    tag_pipeline = next((p for p in pipelines if p["ref"] == "v2.1.1"), None)
    if not tag_pipeline:
        print("\n⚠ No v2.1.1 pipeline found")
        return

    print(f"\n--- Pipeline #{tag_pipeline['id']} Jobs (v2.1.1) ---")
    jobs = api_get(f"/pipelines/{tag_pipeline['id']}/jobs")

    icons = {
        'success': '✅', 'running': '🔄', 'pending': '⏳',
        'created': '⏳', 'failed': '❌', 'manual': '⏸',
        'canceled': '🚫', 'skipped': '⏭',
    }

    # Group by stage
    stages = {}
    for j in jobs:
        stages.setdefault(j['stage'], []).append(j)

    for stage_name in ['test', 'build', 'release']:
        if stage_name not in stages:
            continue
        print(f"\n  [{stage_name}]")
        for j in sorted(stages[stage_name], key=lambda x: x['name']):
            icon = icons.get(j['status'], '?')
            duration = f" ({j['duration']:.0f}s)" if j.get('duration') else ""
            print(f"    {icon} {j['name']}: {j['status']}{duration}")

    # Summary
    all_jobs = [j for j in jobs if j['status'] != 'manual']
    success = sum(1 for j in all_jobs if j['status'] == 'success')
    failed = sum(1 for j in all_jobs if j['status'] == 'failed')
    running = sum(1 for j in all_jobs if j['status'] in ('running', 'pending', 'created'))

    print(f"\n  Summary: {success} passed, {failed} failed, {running} in progress")

    if tag_pipeline['status'] == 'success':
        print("\n✅ Pipeline complete! Release build is ready.")
    elif tag_pipeline['status'] == 'failed':
        print("\n❌ Pipeline failed — check failed jobs above.")
    else:
        print(f"\n🔄 Pipeline still {tag_pipeline['status']}...")


if __name__ == "__main__":
    main()
