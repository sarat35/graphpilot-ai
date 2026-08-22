import type { RecentSearch } from "./types"
import { readStorage, writeStorage, STORAGE_KEYS } from "./storage"
import { SEED_RECENT_SEARCHES } from "./mock-data"

const MAX_RECENT_SEARCHES = 5

/** Reads the five most recent searches, seeding demo history on first use. */
export function getRecentSearches(): RecentSearch[] {
  const existing = readStorage<RecentSearch[] | null>(STORAGE_KEYS.recentSearches, null)
  if (existing) return existing.slice(0, MAX_RECENT_SEARCHES)
  writeStorage(STORAGE_KEYS.recentSearches, SEED_RECENT_SEARCHES)
  return SEED_RECENT_SEARCHES
}

export function addRecentSearch(entry: RecentSearch): RecentSearch[] {
  const current = getRecentSearches()
  const next = [entry, ...current.filter((s) => s.label !== entry.label)].slice(
    0,
    MAX_RECENT_SEARCHES
  )
  writeStorage(STORAGE_KEYS.recentSearches, next)
  return next
}

export function removeRecentSearch(id: string): RecentSearch[] {
  const next = getRecentSearches().filter((s) => s.id !== id)
  writeStorage(STORAGE_KEYS.recentSearches, next)
  return next
}
