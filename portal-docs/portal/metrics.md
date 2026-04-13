# Metrics & Analytics

## SQLite Tables
1. downloads: project, version, asset, timestamp, ip_hash, user_agent
2. clones: project, timestamp, ip_hash, user_agent
3. tool_usage: tool, event (upload/download), timestamp, ip_hash, user_agent
4. catalog_interactions: event, detail, result_count, timestamp, ip_hash

## Umami (self-hosted, port 3001)
Custom events: save_uploaded, save_downloaded, catalog_search, catalog_category, git_clone
No cookies, GDPR-clean, no third-party data sharing

## Internal Dashboard (/metrics)
Protected by METRICS_TOKEN. Downloads, clones, tool usage, top categories/searches.

## Privacy
All IPs hashed with SHA-256 before storage. Raw IPs never written to SQLite.
