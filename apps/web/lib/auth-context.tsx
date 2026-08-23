"use client"

import * as React from "react"
import type { Session } from "./types"
import type { Session as SupabaseSession } from "@supabase/supabase-js"
import { clearStorage, STORAGE_KEYS } from "./storage"
import { createClient, type SupabasePublicConfig } from "./supabase/client"

export class AuthError extends Error {}
export class NetworkError extends Error {}

type SignUpResult = { needsEmailConfirmation: boolean }

interface AuthContextValue {
  session: Session | null
  /** True until the initial session read from storage has completed. */
  isInitializing: boolean
  signIn: (input: { email: string; password: string }) => Promise<void>
  signUp: (input: { name: string; email: string; password: string }) => Promise<SignUpResult>
  signOut: () => Promise<void>
}

const AuthContext = React.createContext<AuthContextValue | null>(null)

function toSession(session: SupabaseSession | null): Session | null {
  if (!session) return null
  return {
    userId: session.user.id,
    name:
      typeof session.user.user_metadata.display_name === "string"
        ? session.user.user_metadata.display_name
        : session.user.email?.split("@")[0] ?? "BuySeconds member",
    email: session.user.email ?? "",
  }
}

function toAuthError(error: unknown): Error {
  if (error instanceof Error && /network|fetch|offline/i.test(error.message)) {
    return new NetworkError("Check your internet connection")
  }
  return new AuthError("Invalid email or password")
}

export function AuthProvider({
  children,
  supabase,
}: {
  children: React.ReactNode
  supabase: SupabasePublicConfig
}) {
  const [session, setSession] = React.useState<Session | null>(null)
  const [isInitializing, setIsInitializing] = React.useState(true)

  React.useEffect(() => {
    const client = createClient(supabase)
    let active = true

    void client.auth.getSession().then(({ data }) => {
      if (active) {
        setSession(toSession(data.session))
        setIsInitializing(false)
      }
    })

    const { data: listener } = client.auth.onAuthStateChange((_event, nextSession) => {
      setSession(toSession(nextSession))
      setIsInitializing(false)
    })

    return () => {
      active = false
      listener.subscription.unsubscribe()
    }
  }, [supabase])

  const signIn = React.useCallback<AuthContextValue["signIn"]>(
    async (input) => {
      const { error } = await createClient(supabase).auth.signInWithPassword(input)
      if (error) throw toAuthError(error)
    },
    [supabase]
  )

  const signUp = React.useCallback<AuthContextValue["signUp"]>(
    async (input) => {
      const { data, error } = await createClient(supabase).auth.signUp({
        email: input.email,
        password: input.password,
        options: {
          data: { display_name: input.name },
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      })
      if (error) throw toAuthError(error)
      return { needsEmailConfirmation: !data.session }
    },
    [supabase]
  )

  const signOut = React.useCallback(async () => {
    const { error } = await createClient(supabase).auth.signOut()
    if (error) throw toAuthError(error)
    setSession(null)
    clearStorage(STORAGE_KEYS.savedCars)
  }, [supabase])

  const value = React.useMemo<AuthContextValue>(
    () => ({ session, isInitializing, signIn, signUp, signOut }),
    [session, isInitializing, signIn, signUp, signOut]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
