import { isAuthed, unauthorized } from "../_lib/auth.js";

export async function onRequestGet({ request, env }) {
  if (!(await isAuthed(request, env))) return unauthorized();

  const totalsQuery = env.DB.prepare(
    `SELECT
       COUNT(DISTINCT c.id) AS total,
       COUNT(DISTINCT CASE WHEN r.label = 'true' THEN c.id END) AS true_count,
       COUNT(DISTINCT CASE WHEN r.label = 'false' THEN c.id END) AS false_count
     FROM candidates c
     LEFT JOIN reviews r ON r.candidate_id = c.id AND r.label IN ('true', 'false')`
  );

  const holdEventsQuery = env.DB.prepare(
    `SELECT COUNT(*) AS hold_events FROM reviews WHERE label = 'hold'`
  );

  const byBatchQuery = env.DB.prepare(
    `SELECT
       c.batch,
       COUNT(DISTINCT c.id) AS total,
       COUNT(DISTINCT CASE WHEN r.label = 'true' THEN c.id END) AS true_count,
       COUNT(DISTINCT CASE WHEN r.label = 'false' THEN c.id END) AS false_count
     FROM candidates c
     LEFT JOIN reviews r ON r.candidate_id = c.id AND r.label IN ('true', 'false')
     GROUP BY c.batch
     ORDER BY c.batch`
  );

  const byReviewerQuery = env.DB.prepare(
    `SELECT reviewer_name, label, COUNT(*) AS cnt
     FROM reviews
     GROUP BY reviewer_name, label
     ORDER BY reviewer_name`
  );

  const recentQuery = env.DB.prepare(
    `SELECT r.candidate_id, r.reviewer_name, r.label, r.reviewed_at, c.batch, c.source
     FROM reviews r
     JOIN candidates c ON c.id = r.candidate_id
     ORDER BY r.reviewed_at DESC
     LIMIT 20`
  );

  const [totals, holdEvents, byBatch, byReviewerRows, recent] = await Promise.all([
    totalsQuery.first(),
    holdEventsQuery.first(),
    byBatchQuery.all(),
    byReviewerQuery.all(),
    recentQuery.all(),
  ]);

  const reviewers = {};
  for (const row of byReviewerRows.results) {
    if (!reviewers[row.reviewer_name]) {
      reviewers[row.reviewer_name] = { reviewer_name: row.reviewer_name, true: 0, false: 0, hold: 0 };
    }
    reviewers[row.reviewer_name][row.label] = row.cnt;
  }

  return new Response(
    JSON.stringify({
      totals: {
        total: totals.total,
        true_count: totals.true_count,
        false_count: totals.false_count,
        pending: totals.total - totals.true_count - totals.false_count,
        hold_events: holdEvents.hold_events,
      },
      by_batch: byBatch.results.map((b) => ({
        batch: b.batch,
        total: b.total,
        true_count: b.true_count,
        false_count: b.false_count,
        pending: b.total - b.true_count - b.false_count,
      })),
      by_reviewer: Object.values(reviewers),
      recent: recent.results,
    }),
    { headers: { "Content-Type": "application/json" } }
  );
}
