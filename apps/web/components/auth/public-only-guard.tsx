"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Spinner } from "@/components/ui/spinner"

/**
 * Wraps pages that should only be visible to signed-out visitors
 * (Landing, Sign In, Sign Up). An authenticated customer is redirected to
 * /search — this is a front-end-only simulation, not real authorization.
 */
export function PublicOnlyGuard({ children }: { children: React.ReactNode }) {
  const { session, isInitializing } = useAuth()
  const router = useRouter()

  React.useEffect(() => {
    if (!isInitializing && session) {
      router.replace("/search")
    }
  }, [isInitializing, session, router])

  if (isInitializing) {
    return null
  }

  if (session) {
    return (
      <div
        role="status"
        className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-sm text-muted-foreground"
      >
        <Spinner />
        <p>You&apos;re already signed in. Taking you to Search…</p>
      </div>
    )
  }

  return <>{children}</>
}
