import { createServerClient } from "@supabase/ssr"
import { cookies } from "next/headers"

function getPublicConfig() {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_PUBLISHABLE_KEY ?? process.env.SUPABASE_ANON_KEY

  if (!url || !key) {
    throw new Error("Supabase server configuration is missing.")
  }

  return { url, key }
}

export async function createClient() {
  const cookieStore = await cookies()
  const { url, key } = getPublicConfig()

  return createServerClient(url, key, {
    cookies: {
      getAll() {
        return cookieStore.getAll()
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        } catch {
          // Server Components cannot mutate cookies. The Proxy refreshes the
          // session for normal browser requests.
        }
      },
    },
  })
}
