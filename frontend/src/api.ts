import { supabase } from "./supabase";

const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  if (!supabase) throw new Error("Supabase n’est pas configuré.");

  const { data, error } = await supabase.auth.getSession();
  if (error) throw error;
  if (!data.session) throw new Error("Une session active est nécessaire.");

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${data.session.access_token}`);
  return fetch(new URL(path.replace(/^\/+/, ""), `${apiBaseUrl}/`), { ...init, headers });
}