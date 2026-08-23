"use client"

import Link from "next/link"
import * as React from "react"
import { useSearchParams } from "next/navigation"
import { ExternalLink, Heart, MapPin, Pencil, SlidersHorizontal } from "lucide-react"
import { getSearchResults, saveVehicle, type ProductSearchResult } from "@/lib/api/product-search"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

export default function ResultsPage() {
  const params = useSearchParams()
  const searchId = params.get("searchId")
  const [results, setResults] = React.useState<ProductSearchResult["results"]>([])
  const [error, setError] = React.useState("")
  const [isLoading, setIsLoading] = React.useState(true)

  React.useEffect(() => {
    if (!searchId) return
    void getSearchResults(searchId)
      .then((response) => setResults(response.results))
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setIsLoading(false))
  }, [searchId])

  if (!searchId) return <EmptyResults />
  if (error) return <div className="mx-auto max-w-5xl px-4 py-10 text-sm text-destructive">{error}</div>
  if (isLoading) return <div className="mx-auto max-w-5xl px-4 py-10 text-sm text-muted-foreground">Loading your ranked matches…</div>
  if (!results.length) return <div className="mx-auto max-w-5xl px-4 py-10"><Badge variant="secondary">No live listings found</Badge><p className="mt-3 text-sm text-muted-foreground">We could not find a product listing in the selected city right now. Try again shortly or adjust the search criteria.</p><Button className="mt-5" render={<Link href="/search" />} nativeButton={false}>Edit search</Button></div>

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-10">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><p className="text-sm font-medium text-primary">Live marketplace listings</p><h1 className="font-heading text-2xl font-semibold tracking-tight">Your best car matches</h1><p className="mt-1 text-sm text-muted-foreground">Ranked city-specific product matches.</p></div>
        <Button variant="outline" render={<Link href="/search" />} nativeButton={false}><Pencil data-icon="inline-start" />Edit search</Button>
      </div>
      <div className="mt-6 flex gap-2 rounded-xl border bg-card p-4 text-sm"><SlidersHorizontal className="size-4 text-muted-foreground" /><span>{results.length} matches</span></div>
      <ol className="mt-6 space-y-3">{results.map((listing, index) => <li key={listing.source_url} className="rounded-xl border bg-card p-4"><div className="flex gap-4"><div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">{index + 1}</div><div className="min-w-0 flex-1"><p className="font-heading text-base font-semibold">{listing.title}</p><p className="mt-1 text-sm text-muted-foreground">{listing.snippet}</p><p className="mt-2 flex items-center gap-1 text-sm text-muted-foreground"><MapPin className="size-3.5" />{listing.source_name}</p><a href={listing.source_url} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-primary underline underline-offset-4">View source <ExternalLink className="size-3.5" /></a></div>{listing.vehicle_id && <Button size="icon" variant="outline" aria-label={`Save ${listing.title}`} onClick={() => void saveVehicle(listing.vehicle_id!)}><Heart /></Button>}</div></li>)}</ol>
    </div>
  )
}

function EmptyResults() { return <div className="mx-auto max-w-5xl px-4 py-10"><Badge variant="secondary">No search selected</Badge><p className="mt-3 text-sm text-muted-foreground">Run a search to see your ranked matches.</p></div> }
