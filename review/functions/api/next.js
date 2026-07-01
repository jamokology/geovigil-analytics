import { isAuthed, unauthorized } from "../_lib/auth.js";

const CLAIM_TTL_MINUTES = 3;

export async function onRequestGet({ request, env }) {
  if (!(await isAuthed(request, env))) return unauthorized();

  const url = new URL(request.url);
  const sessionId = url.searchParams.get("session") || "";

  const { results } = await env.DB.prepare(
    `SELECT c.id, c.image_key, c.source
     FROM candidates c
     WHERE NOT EXISTS (
       SELECT 1 FROM reviews r
       WHERE r.candidate_id = c.id AND r.label IN ('true', 'false')
     )
     AND NOT EXISTS (
       SELECT 1 FROM reviews r2
       WHERE r2.candidate_id = c.id AND r2.label = 'hold' AND r2.session_id = ?
     )
     AND (
       c.claimed_by IS NULL
       OR c.claimed_by = ?
       OR c.claimed_at < datetime('now', '-${CLAIM_TTL_MINUTES} minutes')
     )
     ORDER BY c.batch, c.id
     LIMIT 1`
  )
    .bind(sessionId, sessionId)
    .all();

  const next = results[0] || null;

  if (next) {
    // Soft-lock this candidate to the requesting session so a second
    // reviewer opening the app at the same time isn't served the same
    // image. The lock expires on its own after CLAIM_TTL_MINUTES in case
    // a reviewer closes the tab without submitting a label.
    await env.DB.prepare(
      `UPDATE candidates SET claimed_by = ?, claimed_at = datetime('now') WHERE id = ?`
    )
      .bind(sessionId, next.id)
      .run();
  }

  return new Response(JSON.stringify({ next }), {
    headers: { "Content-Type": "application/json" },
  });
}
