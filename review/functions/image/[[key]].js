import { isAuthed, unauthorized } from "../_lib/auth.js";

export async function onRequestGet({ request, env, params }) {
  if (!(await isAuthed(request, env))) return unauthorized();

  const key = Array.isArray(params.key) ? params.key.join("/") : params.key;
  const object = await env.IMAGES.get(key);
  if (!object) {
    return new Response("not found", { status: 404 });
  }

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set("Cache-Control", "private, max-age=3600");
  return new Response(object.body, { headers });
}
