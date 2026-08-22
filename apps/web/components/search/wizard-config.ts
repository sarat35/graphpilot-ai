import type { FuelType } from "@/lib/types"

export interface WizardStepConfig {
  id: "city" | "budget" | "brand" | "fuel" | "age" | "distance" | "review"
  title: string
  description: string
}

export const WIZARD_STEPS: WizardStepConfig[] = [
  { id: "city", title: "Where are you looking?", description: "We'll match listings in this city." },
  { id: "budget", title: "What's your budget?", description: "Set a price range in Indian rupees." },
  { id: "brand", title: "Any brand preference?", description: "Pick one brand or skip to see all." },
  { id: "fuel", title: "Preferred fuel type?", description: "Pick one or leave it open to all fuel types." },
  { id: "age", title: "How old can the car be?", description: "We'll only show cars within this age." },
  { id: "distance", title: "Maximum kilometres driven?", description: "Cap how much wear and tear you're comfortable with." },
  { id: "review", title: "Review your search", description: "Confirm the details before we compare listings." },
]

export const AGE_OPTIONS = [
  { value: "2", label: "Up to 2 years" },
  { value: "4", label: "Up to 4 years" },
  { value: "6", label: "Up to 6 years" },
  { value: "10", label: "Up to 10 years" },
  { value: "any", label: "Any age" },
]

export const DISTANCE_OPTIONS = [
  { value: "20000", label: "Under 20,000 km" },
  { value: "40000", label: "Under 40,000 km" },
  { value: "60000", label: "Under 60,000 km" },
  { value: "100000", label: "Under 100,000 km" },
  { value: "any", label: "Any distance" },
]

export const FUEL_OPTIONS: { value: FuelType; label: string }[] = [
  { value: "Petrol", label: "Petrol" },
  { value: "Diesel", label: "Diesel" },
  { value: "CNG", label: "CNG" },
  { value: "Electric", label: "Electric" },
  { value: "Hybrid", label: "Hybrid" },
]

export function formatInr(value: number) {
  return `₹${value.toLocaleString("en-IN")}`
}
