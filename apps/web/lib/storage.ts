// Thin, SSR-safe wrappers around window.localStorage used to persist the
// prototype's simulated session and app state. There is no server-side
// persistence — everything here is browser-local demonstration state.

export const STORAGE_KEYS = {
  session: "buyseconds:session",
  recentSearches: "buyseconds:recent-searches",
  savedCars: "buyseconds:saved-cars",
  chatDraft: "buyseconds:chat-draft",
} as const

export function readStorage<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback
  try {
    const raw = window.localStorage.getItem(key)
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export function writeStorage<T>(key: string, value: T): void {
  if (typeof window === "undefined") return
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // Ignore write failures (e.g. storage disabled) — the prototype should
    // continue to function using in-memory state for that session.
  }
}

export function clearStorage(key: string): void {
  if (typeof window === "undefined") return
  try {
    window.localStorage.removeItem(key)
  } catch {
    // no-op
  }
}

/** Simulates network/async latency so loading states feel real. */
export function simulateDelay(ms = 700): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
