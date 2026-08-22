"use client"

import * as React from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Spinner } from "@/components/ui/spinner"

/**
 * Wraps every protected page (Search, Results, Product, My Products,
 * Chatbot, Account). A visitor without a simulated session is redirected to
 * /auth/signin with the original destination preserved in ?from=.
 */
export function ProtectedGuard({ children }: { children: React.ReactNode }) {
  const { session, isInitializing } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  React.useEffect(() => {
    if (!isInitializing && !session) {
      const from = encodeURIComponent(pathname || "/search")
      router.replace(`/auth/signin?from=${from}`)
    }
  }, [isInitializing, session, router, pathname])

  if (isInitializing) {
    return null
  }

  if (!session) {
    return (
      <div
        role="status"
        className="flex min-h-svh flex-col items-center justify-center gap-3 bg-background text-sm text-muted-foreground"
      >
        <Spinner />
        <p>Redirecting you to sign in…</p>
      </div>
    )
  }

  return <>{children}</>
}
