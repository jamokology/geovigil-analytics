# GeoVigil Analytics — Candidate Review Tool

Mobile-first swipe UI for staff to label the ~1500 detection candidates
(see [CONCEPT_NOTE.md](../doc/CONCEPT_NOTE.md), "構築フロー") as True/False.
Swipe right = True, left = False, up = Hold (skip for this session only —
held candidates resurface in the next session).

Separate Cloudflare Pages project from the main dashboard (`web/`), backed
by Cloudflare R2 (images) and D1 (review results).

## One-time setup

```bash
npm install -g wrangler
wrangler login

cd review
wrangler r2 bucket create geovigil-review-images
wrangler d1 create geovigil-review   # copy the printed database_id into wrangler.toml
wrangler d1 execute geovigil-review --remote --file=./schema.sql

# Create the Pages project and set the shared passphrase
wrangler pages project create geovigil-review
wrangler pages secret put REVIEW_PASSPHRASE --project-name geovigil-review
```

Deploy:

```bash
wrangler pages deploy public --project-name geovigil-review
```

## Loading candidates (from the workstation)

Each batch (Sentinel candidates / existing-model candidates / Sentinel-triggered
NICFI candidates — see CONCEPT_NOTE "構築フロー" steps 2/3a/3b) is uploaded with:

```bash
uv run python py/pipeline/upload_candidates.py \
    --manifest step2_candidates.csv \
    --batch step2-2025-06-08
```

`step2_candidates.csv` columns: `image_path,source,lat,lon`
(`source` is one of `sentinel_candidate`, `existing_model`, `sentinel_triggered_nicfi`).

Batches can be uploaded incrementally — e.g. step 3b's manifest only needs to
exist once step 2's results are ready, per the CONCEPT_NOTE dependency.
Newly uploaded candidates appear in the review site immediately; no
redeploy needed.

## Pulling results back for the threshold/distribution analysis

```bash
wrangler d1 execute geovigil-review --remote --json --command \
  "SELECT c.id, c.source, c.batch, c.lat, c.lon, r.label, r.reviewer_name, r.reviewed_at
   FROM candidates c
   JOIN reviews r ON r.candidate_id = c.id
   WHERE r.label IN ('true','false')" > results.json
```

(If a candidate was reviewed more than once — e.g. two staff picked up the
same item before either finished — this returns one row per review; the
CONCEPT_NOTE threshold-fitting step should dedupe by `id`, keeping the most
recent `reviewed_at`.)

## Design notes

- **Auth:** name entry + one shared passphrase (`REVIEW_PASSPHRASE`), no
  per-user accounts — appropriate for a small (2-5 person) trusted staff
  group. The passphrase gates both the API and the `/image/*` proxy, so the
  R2 bucket itself stays private and candidate coordinates are never
  exposed in a public URL.
- **No claim/locking:** with only a few reviewers, occasional duplicate
  labeling of the same candidate is an acceptable trade-off for a much
  simpler "serve the next unlabeled item" query.
- **Hold semantics:** a `hold` review is scoped to `session_id` (a random
  ID generated per browser session), so it's excluded from that reviewer's
  queue only until they reload/reopen the app.
