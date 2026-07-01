import { isAuthed, unauthorized } from "../_lib/auth.js";

const VALID_LABELS = new Set(["true", "false", "hold"]);

export async function onRequestPost({ request, env }) {
  if (!(await isAuthed(request, env))) return unauthorized();

  const body = await request.json().catch(() => ({}));
  const { candidate_id, reviewer_name, label, session_id } = body;

  if (!candidate_id || !reviewer_name || !session_id || !VALID_LABELS.has(label)) {
    return new Response(JSON.stringify({ error: "invalid request" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  await env.DB.batch([
    env.DB.prepare(
      `INSERT INTO reviews (candidate_id, reviewer_name, label, session_id)
       VALUES (?, ?, ?, ?)`
    ).bind(candidate_id, reviewer_name.trim(), label, session_id),
    // Release the claim immediately (rather than waiting out the TTL) so a
    // held candidate can be picked up by another reviewer's session right away.
    env.DB.prepare(
      `UPDATE candidates SET claimed_by = NULL, claimed_at = NULL WHERE id = ?`
    ).bind(candidate_id),
  ]);

  return new Response(JSON.stringify({ ok: true }), {
    headers: { "Content-Type": "application/json" },
  });
}
