"use client"

import * as React from "react"
import { CheckCircle2Icon, MapPinIcon, ChevronLeftIcon, ChevronRightIcon, SearchIcon } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Field, FieldLabel, FieldDescription, FieldGroup } from "@/components/ui/field"
import { InputGroup, InputGroupInput, InputGroupAddon } from "@/components/ui/input-group"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { StepProgress } from "@/components/search/step-progress"
import { RecentSearchesPanel } from "@/components/search/recent-searches-panel"
import { WIZARD_STEPS, AGE_OPTIONS, DISTANCE_OPTIONS, FUEL_OPTIONS, formatInr } from "@/components/search/wizard-config"
import { BRANDS, CITIES } from "@/lib/mock-data"
import { getRecentSearches, addRecentSearch, removeRecentSearch } from "@/lib/recent-searches"
import type { FuelType, RecentSearch, SearchCriteria } from "@/lib/types"

type WizardState = {
  city: string
  minPrice: string
  maxPrice: string
  brand: string | null
  fuelType: FuelType | null
  maxAgeYears: string | null
  maxKilometres: string | null
}

const INITIAL_STATE: WizardState = {
  city: "",
  minPrice: "",
  maxPrice: "",
  brand: null,
  fuelType: null,
  maxAgeYears: null,
  maxKilometres: null,
}

function criteriaFromState(state: WizardState): SearchCriteria {
  return {
    city: state.city,
    minPrice: state.minPrice ? Number(state.minPrice) : undefined,
    maxPrice: state.maxPrice ? Number(state.maxPrice) : undefined,
    brand: state.brand ?? undefined,
    fuelType: state.fuelType ?? undefined,
    maxAgeYears:
      state.maxAgeYears && state.maxAgeYears !== "any" ? Number(state.maxAgeYears) : undefined,
    maxKilometres:
      state.maxKilometres && state.maxKilometres !== "any" ? Number(state.maxKilometres) : undefined,
  }
}

function labelForCriteria(criteria: SearchCriteria): string {
  const parts: string[] = []
  if (criteria.brand) parts.push(criteria.brand)
  parts.push(criteria.city || "Any city")
  if (criteria.maxPrice) parts.push(`under ${formatInr(criteria.maxPrice)}`)
  if (criteria.fuelType) parts.push(criteria.fuelType)
  return parts.join(", ")
}

export function SearchWizard() {
  const [stepIndex, setStepIndex] = React.useState(0)
  const [state, setState] = React.useState<WizardState>(INITIAL_STATE)
  const [recentSearches, setRecentSearches] = React.useState<RecentSearch[]>([])
  const [submitted, setSubmitted] = React.useState<SearchCriteria | null>(null)

  React.useEffect(() => {
    setRecentSearches(getRecentSearches())
  }, [])

  const step = WIZARD_STEPS[stepIndex]
  const isFirstStep = stepIndex === 0
  const isReviewStep = step.id === "review"

  function goNext() {
    setStepIndex((i) => Math.min(i + 1, WIZARD_STEPS.length - 1))
  }
  function goBack() {
    setStepIndex((i) => Math.max(i - 1, 0))
  }

  function canProceed() {
    switch (step.id) {
      case "city":
        return state.city.trim().length > 0
      default:
        return true
    }
  }

  function applyRecentSearch(search: RecentSearch) {
    setState({
      city: search.criteria.city ?? "",
      minPrice: search.criteria.minPrice?.toString() ?? "",
      maxPrice: search.criteria.maxPrice?.toString() ?? "",
      brand: search.criteria.brand ?? null,
      fuelType: search.criteria.fuelType ?? null,
      maxAgeYears: search.criteria.maxAgeYears?.toString() ?? null,
      maxKilometres: search.criteria.maxKilometres?.toString() ?? null,
    })
    setStepIndex(WIZARD_STEPS.length - 1)
    setSubmitted(null)
  }

  function removeSearch(id: string) {
    setRecentSearches(removeRecentSearch(id))
  }

  function handleSubmit() {
    const criteria = criteriaFromState(state)
    const entry: RecentSearch = {
      id: `search-${Date.now()}`,
      criteria,
      label: labelForCriteria(criteria),
      createdAt: new Date().toISOString(),
      resultCount: 5,
    }
    setRecentSearches(addRecentSearch(entry))
    setSubmitted(criteria)
    toast.success("Search saved", {
      description: "Comparing your top 5 matches is coming in the next build step.",
    })
  }

  function startOver() {
    setState(INITIAL_STATE)
    setSubmitted(null)
    setStepIndex(0)
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <div className="rounded-xl border border-border bg-card p-6 sm:p-8">
        <StepProgress currentIndex={stepIndex} />

        <div className="mt-6">
          <h1 className="font-heading text-xl font-semibold tracking-tight">{step.title}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{step.description}</p>
        </div>

        <div className="mt-6 min-h-56">
          {submitted ? (
            <SubmittedSummary criteria={submitted} onStartOver={startOver} />
          ) : (
            <>
              {step.id === "city" && (
                <Field>
                  <FieldLabel htmlFor="city-select">City</FieldLabel>
                  <Select value={state.city || null} onValueChange={(value) => setState((s) => ({ ...s, city: value ?? "" }))}>
                    <SelectTrigger id="city-select" className="w-full">
                      <MapPinIcon className="size-4 text-muted-foreground" data-icon="inline-start" />
                      <SelectValue placeholder="Choose a city" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        {CITIES.map((city) => (
                          <SelectItem key={city} value={city}>
                            {city}
                          </SelectItem>
                        ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                  <FieldDescription>Demo listings are only available in these cities.</FieldDescription>
                </Field>
              )}

              {step.id === "budget" && (
                <FieldGroup>
                  <Field>
                    <FieldLabel htmlFor="min-price">Minimum price</FieldLabel>
                    <InputGroup>
                      <InputGroupAddon>₹</InputGroupAddon>
                      <InputGroupInput
                        id="min-price"
                        type="number"
                        inputMode="numeric"
                        placeholder="0"
                        value={state.minPrice}
                        onChange={(e) => setState((s) => ({ ...s, minPrice: e.target.value }))}
                      />
                    </InputGroup>
                  </Field>
                  <Field>
                    <FieldLabel htmlFor="max-price">Maximum price</FieldLabel>
                    <InputGroup>
                      <InputGroupAddon>₹</InputGroupAddon>
                      <InputGroupInput
                        id="max-price"
                        type="number"
                        inputMode="numeric"
                        placeholder="1,500,000"
                        value={state.maxPrice}
                        onChange={(e) => setState((s) => ({ ...s, maxPrice: e.target.value }))}
                      />
                    </InputGroup>
                    <FieldDescription>Leave blank if you don&apos;t have an upper limit.</FieldDescription>
                  </Field>
                </FieldGroup>
              )}

              {step.id === "brand" && (
                <Field>
                  <FieldLabel htmlFor="brand-select">Brand</FieldLabel>
                  <Select
                    value={state.brand}
                    onValueChange={(value) => setState((s) => ({ ...s, brand: value }))}
                  >
                    <SelectTrigger id="brand-select" className="w-full">
                      <SelectValue placeholder="Any brand" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        {BRANDS.map((brand) => (
                          <SelectItem key={brand} value={brand}>
                            {brand}
                          </SelectItem>
                        ))}
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                  <FieldDescription>Skip this to compare cars across every brand.</FieldDescription>
                </Field>
              )}

              {step.id === "fuel" && (
                <Field>
                  <FieldLabel>Fuel type</FieldLabel>
                  <ToggleGroup
                    variant="outline"
                    value={state.fuelType ? [state.fuelType] : []}
                    onValueChange={(value: string[]) =>
                      setState((s) => ({ ...s, fuelType: (value[0] as FuelType) ?? null }))
                    }
                    className="flex-wrap"
                  >
                    {FUEL_OPTIONS.map((option) => (
                      <ToggleGroupItem key={option.value} value={option.value}>
                        {option.label}
                      </ToggleGroupItem>
                    ))}
                  </ToggleGroup>
                  <FieldDescription>Select one, or leave all unselected for any fuel type.</FieldDescription>
                </Field>
              )}

              {step.id === "age" && (
                <Field>
                  <FieldLabel>Maximum age</FieldLabel>
                  <ToggleGroup
                    variant="outline"
                    value={state.maxAgeYears ? [state.maxAgeYears] : []}
                    onValueChange={(value: string[]) =>
                      setState((s) => ({ ...s, maxAgeYears: value[0] ?? null }))
                    }
                    className="flex-wrap"
                  >
                    {AGE_OPTIONS.map((option) => (
                      <ToggleGroupItem key={option.value} value={option.value}>
                        {option.label}
                      </ToggleGroupItem>
                    ))}
                  </ToggleGroup>
                </Field>
              )}

              {step.id === "distance" && (
                <Field>
                  <FieldLabel>Maximum kilometres driven</FieldLabel>
                  <ToggleGroup
                    variant="outline"
                    value={state.maxKilometres ? [state.maxKilometres] : []}
                    onValueChange={(value: string[]) =>
                      setState((s) => ({ ...s, maxKilometres: value[0] ?? null }))
                    }
                    className="flex-wrap"
                  >
                    {DISTANCE_OPTIONS.map((option) => (
                      <ToggleGroupItem key={option.value} value={option.value}>
                        {option.label}
                      </ToggleGroupItem>
                    ))}
                  </ToggleGroup>
                </Field>
              )}

              {step.id === "review" && <ReviewStep state={state} />}
            </>
          )}
        </div>

        {!submitted && (
          <>
            <Separator className="my-6" />
            <div className="flex items-center justify-between">
              <Button type="button" variant="ghost" onClick={goBack} disabled={isFirstStep}>
                <ChevronLeftIcon data-icon="inline-start" />
                Back
              </Button>
              {isReviewStep ? (
                <Button type="button" onClick={handleSubmit}>
                  <SearchIcon data-icon="inline-start" />
                  Compare top matches
                </Button>
              ) : (
                <Button type="button" onClick={goNext} disabled={!canProceed()}>
                  Continue
                  <ChevronRightIcon data-icon="inline-end" />
                </Button>
              )}
            </div>
          </>
        )}
      </div>

      <RecentSearchesPanel searches={recentSearches} onApply={applyRecentSearch} onRemove={removeSearch} />
    </div>
  )
}

function ReviewStep({ state }: { state: WizardState }) {
  const rows: { label: string; value: string }[] = [
    { label: "City", value: state.city || "Any city" },
    {
      label: "Budget",
      value:
        state.minPrice || state.maxPrice
          ? `${state.minPrice ? formatInr(Number(state.minPrice)) : "₹0"} – ${
              state.maxPrice ? formatInr(Number(state.maxPrice)) : "No limit"
            }`
          : "No limit",
    },
    { label: "Brand", value: state.brand ?? "Any brand" },
    { label: "Fuel type", value: state.fuelType ?? "Any fuel type" },
    {
      label: "Maximum age",
      value: state.maxAgeYears && state.maxAgeYears !== "any" ? `${state.maxAgeYears} years` : "Any age",
    },
    {
      label: "Maximum distance",
      value:
        state.maxKilometres && state.maxKilometres !== "any"
          ? `${Number(state.maxKilometres).toLocaleString("en-IN")} km`
          : "Any distance",
    },
  ]

  return (
    <dl className="flex flex-col divide-y divide-border rounded-lg border border-border">
      {rows.map((row) => (
        <div key={row.label} className="flex items-center justify-between gap-4 px-4 py-3 text-sm">
          <dt className="text-muted-foreground">{row.label}</dt>
          <dd className="font-medium text-foreground">{row.value}</dd>
        </div>
      ))}
    </dl>
  )
}

function SubmittedSummary({
  criteria,
  onStartOver,
}: {
  criteria: SearchCriteria
  onStartOver: () => void
}) {
  return (
    <div className="flex flex-col items-start gap-4 rounded-lg border border-dashed border-border bg-secondary/40 p-6">
      <Badge variant="secondary" className="gap-1.5">
        <CheckCircle2Icon className="size-3.5" aria-hidden="true" />
        Search saved
      </Badge>
      <p className="text-sm leading-relaxed text-muted-foreground">
        We saved &ldquo;{labelForCriteria(criteria)}&rdquo; to your recent searches. The ranked
        comparison results page is coming in the next build step of this prototype.
      </p>
      <Button type="button" variant="outline" onClick={onStartOver}>
        Start a new search
      </Button>
    </div>
  )
}
