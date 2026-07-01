-- D1 schema for the candidate review (swipe) tool.
-- Apply with: wrangler d1 execute geovigil-review --remote --file=./schema.sql

CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY,          -- e.g. "s2-000123", "nicfi-000045", "s2trig-000045"
  image_key TEXT NOT NULL,      -- R2 object key
  source TEXT NOT NULL,         -- 'sentinel_candidate' | 'existing_model' | 'sentinel_triggered_nicfi'
  batch TEXT NOT NULL,          -- e.g. "step2-2025-06-08", "step3a-2025-06-15", "step3b-2025-06-15"
  lat REAL,
  lon REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  claimed_by TEXT,               -- session_id currently holding this candidate (soft lock)
  claimed_at TEXT                -- claim expires after a few minutes (see functions/api/next.js)
);

CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL REFERENCES candidates(id),
  reviewer_name TEXT NOT NULL,
  label TEXT NOT NULL,          -- 'true' | 'false' | 'hold'
  session_id TEXT NOT NULL,
  reviewed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reviews_candidate ON reviews(candidate_id);
CREATE INDEX IF NOT EXISTS idx_reviews_label ON reviews(candidate_id, label);
