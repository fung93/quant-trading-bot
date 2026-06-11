import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

/**
 * Anon-key client, created lazily at request time (a module-level throw
 * would break `next build` when env vars are absent). RLS restricts this
 * key to read-only access on `candles` — the service role key must never
 * appear anywhere in dashboard/ or in Vercel env vars.
 */
export function getSupabase(): SupabaseClient {
  if (client) return client;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY - " +
        "copy dashboard/.env.example to dashboard/.env.local and fill it in " +
        "(or set them in Vercel project settings)."
    );
  }

  client = createClient(url, anonKey, {
    auth: { persistSession: false },
  });
  return client;
}
