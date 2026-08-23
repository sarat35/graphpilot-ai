"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { Heart, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { getRecentSearches } from "@/lib/recent-searches"

export default function ProductsPage() {
  const router = useRouter()
  const searches = getRecentSearches()
  return <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-10"><p className="text-sm font-medium text-primary">My shortlist</p><h1 className="font-heading text-2xl font-semibold">My Products</h1><section className="mt-6 rounded-xl border bg-card p-6"><div className="flex size-10 items-center justify-center rounded-full bg-muted"><Heart className="size-5" /></div><h2 className="mt-4 font-heading text-lg font-semibold">No saved cars yet</h2><p className="mt-1 text-sm text-muted-foreground">Save up to five cars while comparing your matches.</p><Button className="mt-5" render={<Link href="/search" />} nativeButton={false}><Search data-icon="inline-start" />Start a search</Button></section><section className="mt-8"><h2 className="font-heading text-lg font-semibold">Recent searches</h2><div className="mt-3 max-w-xl space-y-2">{searches.map((search) => <button key={search.id} onClick={() => router.push(`/results?city=${encodeURIComponent(search.criteria.city)}`)} className="w-full rounded-lg border bg-card p-3 text-left text-sm hover:bg-accent/30"><span className="font-medium">{search.label}</span><span className="mt-1 block text-muted-foreground">View five saved demo matches</span></button>)}</div></section></div>
}
