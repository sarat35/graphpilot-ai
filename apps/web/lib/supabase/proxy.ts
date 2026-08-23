import { createServerClient } from "@supabase/ssr"
import { NextResponse, type NextRequest } from "next/server"

const PROTECTED_PREFIXES = [
  "/search",
  "/results",
  "/product",
  "/products",
  "/chatbot",
  "/account",
]
const PUBLIC_ONLY_PATHS = new Set(["/", "/auth/signin", "/auth/signup"])

function isProtectedPath(pathname: string) {
  return PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  )
}

function copyCookies(from: NextResponse, to: NextResponse) {
  from.cookies.getAll().forEach((cookie) => to.cookies.set(cookie))
  return to
}

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request })
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_PUBLISHABLE_KEY ?? process.env.SUPABASE_ANON_KEY

  if (!url || !key) return response
  if (!URL.canParse(url)) return response

  const supabase = createServerClient(url, key, {
    cookies: {
      getAll() {
        return request.cookies.getAll()
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
        response = NextResponse.next({ request })
        cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options))
      },
    },
  })

  const { data: claimsResult } = await supabase.auth.getClaims()
  const isAuthenticated = Boolean(claimsResult?.claims?.sub)
  const { pathname, search } = request.nextUrl

  if (!isAuthenticated && isProtectedPath(pathname)) {
    const signInUrl = request.nextUrl.clone()
    signInUrl.pathname = "/auth/signin"
    signInUrl.searchParams.set("from", `${pathname}${search}`)
    return copyCookies(response, NextResponse.redirect(signInUrl))
  }

  if (isAuthenticated && PUBLIC_ONLY_PATHS.has(pathname)) {
    const searchUrl = request.nextUrl.clone()
    searchUrl.pathname = "/search"
    searchUrl.search = ""
    return copyCookies(response, NextResponse.redirect(searchUrl))
  }

  return response
}
