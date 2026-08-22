// Shared front-end-only types for the BuySeconds prototype.
// All data modeled here is demonstration data — there is no backend.

export type FuelType = "Petrol" | "Diesel" | "CNG" | "Electric" | "Hybrid"

export type Transmission = "Manual" | "Automatic"

export type SellerType = "Dealer" | "Certified Dealer" | "Individual"

export interface Car {
  id: string
  make: string
  model: string
  variant: string
  year: number
  fuelType: FuelType
  transmission: Transmission
  price: number
  kilometres: number
  city: string
  image: string
  marketplaceName: string
  sourceUrl: string
  sellerType: SellerType
  postedDate: string // ISO date string
  availability: "Available" | "Expired"
  features: string[]
  description: string
  conditionNotes: string
}

export interface RankedCar extends Car {
  matchPercentage: number
  matchReasons: string[]
  unmatchedReasons: string[]
}

export interface SearchCriteria {
  city: string
  minPrice?: number
  maxPrice?: number
  brand?: string
  fuelType?: FuelType
  maxAgeYears?: number
  maxKilometres?: number
}

export interface RecentSearch {
  id: string
  criteria: SearchCriteria
  label: string
  createdAt: string // ISO date string
  resultCount: number
}

export interface MockUser {
  id: string
  name: string
  email: string
  password: string
  defaultCity?: string
}

export interface Session {
  userId: string
  name: string
  email: string
}

export type ChatRole = "assistant" | "user"

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  createdAt: string
  suggestedReplies?: string[]
}

export type AsyncState = "idle" | "loading" | "success" | "empty" | "error" | "offline"
