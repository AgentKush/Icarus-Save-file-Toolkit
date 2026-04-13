#!/bin/bash
# ============================================================================
# GitLab Upload Janitor
# ============================================================================
# Cleans up orphaned uploads on the GitLab Omnibus server.
# Orphaned uploads are files that were uploaded but never referenced
# in any issue, MR, wiki page, or comment.
#
# SETUP (on the GitLab server):
#   1. Copy to server:
#      sudo cp gitlab_upload_janitor.sh /opt/gitlab/bin/
#      sudo chmod +x /opt/gitlab/bin/gitlab_upload_janitor.sh
#
#   2. Add cron job (runs every 6 hours):
#      sudo crontab -e
#      0 */6 * * * /opt/gitlab/bin/gitlab_upload_janitor.sh >> /var/log/gitlab/upload_janitor.log 2>&1
#
# MANUAL RUN:
#   # Dry run (report only, no deletions):
#   sudo /opt/gitlab/bin/gitlab_upload_janitor.sh --dry-run
#
#   # Live run (actually delete orphans):
#   sudo /opt/gitlab/bin/gitlab_upload_janitor.sh
# ============================================================================

set -euo pipefail

DRY_RUN="false"
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN="true"
fi

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [upload-janitor] $*"
}

log "Starting orphan upload cleanup (DRY_RUN=$DRY_RUN)..."

# Use GitLab's built-in rake task for orphaned project uploads
log "Running gitlab-rake gitlab:cleanup:project_uploads..."
gitlab-rake gitlab:cleanup:project_uploads DRY_RUN="$DRY_RUN" 2>&1 | while IFS= read -r line; do
    log "  $line"
done

# Also clean up orphaned LFS objects for both projects
for pid in 1 2; do
    log "Running gitlab-rake gitlab:cleanup:orphan_lfs_file_references PROJECT_ID=$pid..."
    gitlab-rake gitlab:cleanup:orphan_lfs_file_references PROJECT_ID="$pid" DRY_RUN="$DRY_RUN" 2>&1 | while IFS= read -r line; do
        log "  $line"
    done
done

log "Cleanup complete."
