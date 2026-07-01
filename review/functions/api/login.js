import { sha256Hex } from "../_lib/auth.js";

export async function onRequestPost({ request, env }) {
  const { passphrase } = await request.json().catch(() => ({}));
  if (!passphrase || passphrase !== env.REVIEW_PASSPHRASE) {
    return new Response(JSON.stringify({ error: "invalid passphrase" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const token = await sha256Hex(env.REVIEW_PASSPHRASE);
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Set-Cookie": `gv_auth=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=2592000`,
    },
  });
}
