import { createClient } from "@/lib/supabase/client"
import type { FuelType, SearchCriteria } from "@/lib/types"

type ApiFuelType = Lowercase<FuelType>

export type ProductSearchResult = {
  query: string
  results: Array<{
    vehicle_id: string | null
    title: string
    source_url: string
    source_name: string
    snippet: string
    price_inr: number | null
    year: number | null
    kilometres: number | null
  }>
  result_source: string
  model_name: string
  request_id: string
}

export type Vehicle = {
  id: string
  make: string
  model: string
  variant: string
  year: number
  fuel_type: string
  transmission: string
  price_inr: number
  kilometres: number
  city: string
  source_name: string
  source_url: string
  seller_type: string
  description: string
  condition_notes: string
}

export type SavedVehicle = { id: string; vehicle: Vehicle; saved_at: string }

export type ConversationDetail = {
  conversation: { id: string; status: string; criteria: Record<string, string>; last_message_at: string }
  messages: Array<{ id: string; role: "user" | "assistant"; content: string; created_at: string }>
  model_name: string
}

export type SearchSummary = {
  id: string
  city: string
  brand: string | null
  model: string | null
  fuel_type: string | null
  status: "ready" | "empty"
  result_count: number
  created_at: string
}

function getSupabaseConfig() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY

  if (!url || !key) {
    throw new Error("Supabase browser configuration is missing.")
  }

  return { url, key }
}

async function getAccessToken() {
  const { data } = await createClient(getSupabaseConfig()).auth.getSession()
  const accessToken = data.session?.access_token

  if (!accessToken) {
    throw new Error("Please sign in before searching.")
  }

  return accessToken
}

function toSearchRequest(criteria: SearchCriteria) {
  return {
    city: criteria.city,
    min_price_inr: criteria.minPrice,
    max_price_inr: criteria.maxPrice,
    brand: criteria.brand,
    model: criteria.model,
    fuel_type: criteria.fuelType?.toLowerCase() as ApiFuelType | undefined,
    max_age_years: criteria.maxAgeYears,
    max_kilometres: criteria.maxKilometres,
  }
}

async function postAuthenticated<T>(path: string, criteria: SearchCriteria): Promise<T> {
  const accessToken = await getAccessToken()
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1${path}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(toSearchRequest(criteria)),
    }
  )

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail ?? "We could not complete the product search.")
  }

  return response.json() as Promise<T>
}

export async function createProductSearch(criteria: SearchCriteria): Promise<ProductSearchResult> {
  return postAuthenticated<ProductSearchResult>("/product-search", criteria)
}

export async function createSearch(criteria: SearchCriteria): Promise<SearchSummary> {
  const response = await postAuthenticated<{ search: SearchSummary }>("/searches", criteria)
  return response.search
}

async function requestAuthenticated<T>(path: string, init?: RequestInit): Promise<T> {
  const accessToken = await getAccessToken()
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json", ...init?.headers },
  })
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(detail?.detail ?? "We could not complete the request.")
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T)
}

export async function getSearchResults(searchId: string): Promise<{ search: SearchSummary; results: ProductSearchResult["results"] }> {
  return requestAuthenticated(`/searches/${searchId}/results`)
}

export async function getVehicle(vehicleId: string): Promise<Vehicle> {
  return requestAuthenticated(`/vehicles/${vehicleId}`)
}

export async function listSavedVehicles(): Promise<SavedVehicle[]> {
  return requestAuthenticated("/saved-vehicles")
}

export async function saveVehicle(vehicleId: string): Promise<SavedVehicle> {
  return requestAuthenticated("/saved-vehicles", { method: "POST", body: JSON.stringify({ vehicle_id: vehicleId }) })
}

export async function removeSavedVehicle(vehicleId: string): Promise<void> {
  return requestAuthenticated(`/saved-vehicles/${vehicleId}`, { method: "DELETE" })
}

export async function createConversation(): Promise<ConversationDetail> {
  return requestAuthenticated("/conversations", { method: "POST" })
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  return requestAuthenticated(`/conversations/${conversationId}`)
}

export async function sendConversationMessage(conversationId: string, content: string): Promise<ConversationDetail> {
  return requestAuthenticated(`/conversations/${conversationId}/messages`, { method: "POST", body: JSON.stringify({ content }) })
}
