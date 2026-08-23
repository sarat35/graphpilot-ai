import { createBrowserClient } from "@supabase/ssr"

export type SupabasePublicConfig = {
  url: string
  key: string
}

function validatePublicConfig({ url, key }: SupabasePublicConfig) {
  if (!url || !key) {
    throw new Error("Supabase browser configuration is missing.")
  }
  if (!URL.canParse(url)) {
    throw new Error("Supabase browser URL is invalid.")
  }

  return { url, key }
}

export function createClient(config: SupabasePublicConfig) {
  const { url, key } = validatePublicConfig(config)
  return createBrowserClient(url, key)
}
