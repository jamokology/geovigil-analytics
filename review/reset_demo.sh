#!/bin/sh
# Reset the demo batch so it can be reviewed again from scratch.
# Usage: ./reset_demo.sh
set -e
cd "$(dirname "$0")"
wrangler d1 execute geovigil-review --remote --command \
  "DELETE FROM reviews WHERE candidate_id LIKE 'demo-2026-07-01-%';"
echo "Demo batch reset. All 10 demo images are unlabeled again."
