"use client"

import * as React from "react"
import type { Session } from "./types"
import { readStorage, writeStorage, clearStorage, STORAGE_KEYS } from "./storage"
import { AuthError, NetworkError, mockSignIn, mockSignUp } from "./mock-auth"

interface AuthContextValue {
  session: Session | null
  /** True until the initial session read from storage has completed. */
  isInitializing: boolean
  signIn: (input: { email: string; password: string }) => Promise<void>
  signUp: (input: { name: string; email: string; password: string }) => Promise<void>
  signOut: () => void
}

const AuthContext = React.createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = React.useState<Session | null>(null)
  const [isInitializing, setIsInitializing] = React.useState(true)

  React.useEffect(() => {
    setSession(readStorage<Session | null>(STORAGE_KEYS.session, null))
    setIsInitializing(false)
  }, [])

  const persistSession = React.useCallback((next: Session) => {
    setSession(next)
    writeStorage(STORAGE_KEYS.session, next)
  }, [])

  const signIn = React.useCallback<AuthContextValue["signIn"]>(
    async (input) => {
      const result = await mockSignIn(input)
      persistSession(result)
    },
    [persistSession]
  )

  const signUp = React.useCallback<AuthContextValue["signUp"]>(
    async (input) => {
      const result = await mockSignUp(input)
      persistSession(result)
    },
    [persistSession]
  )

  const signOut = React.useCallback(() => {
    setSession(null)
    clearStorage(STORAGE_KEYS.session)
    clearStorage(STORAGE_KEYS.savedCars)
  }, [])

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

export { AuthError, NetworkError }
