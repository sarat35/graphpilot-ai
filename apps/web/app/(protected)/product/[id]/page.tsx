"use client"

import Link from "next/link"
import { useParams } from "next/navigation"
import { ExternalLink, Heart, MapPin } from "lucide-react"
import { MOCK_CARS } from "@/lib/mock-data"
import { formatInr } from "@/components/search/wizard-config"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export default function ProductPage() {
  const { id } = useParams<{ id: string }>()
  const car = MOCK_CARS.find((item) => item.id === id)
  if (!car) return <div className="mx-auto max-w-3xl px-4 py-16"><h1 className="font-heading text-2xl font-semibold">This demo listing is no longer available.</h1><Button className="mt-6" render={<Link href="/results" />} nativeButton={false}>Back to results</Button></div>
  return <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-10"><Link className="text-sm text-primary hover:underline" href="/results">← Results</Link><div className="mt-5 rounded-xl border bg-card p-6"><div className="flex flex-wrap justify-between gap-4"><div><p className="text-sm text-primary">Demo listing · {car.marketplaceName}</p><h1 className="font-heading text-2xl font-semibold">{car.make} {car.model} {car.variant}</h1><p className="mt-2 text-xl font-semibold">{formatInr(car.price)}</p></div><Badge className="h-fit">Strong match</Badge></div><div className="mt-6 grid gap-3 text-sm sm:grid-cols-3"><p><span className="text-muted-foreground">Year</span><br />{car.year}</p><p><span className="text-muted-foreground">Fuel & transmission</span><br />{car.fuelType} · {car.transmission}</p><p><span className="text-muted-foreground">Distance</span><br />{car.kilometres.toLocaleString("en-IN")} km</p></div><p className="mt-6 flex items-center gap-1 text-sm"><MapPin className="size-4 text-muted-foreground" />{car.city} · {car.sellerType}</p><p className="mt-6 text-sm text-muted-foreground">{car.description}</p><div className="mt-6 rounded-lg bg-muted p-4 text-sm"><p className="font-medium">Condition notes</p><p className="mt-1 text-muted-foreground">{car.conditionNotes}</p></div><div className="mt-6 flex flex-wrap gap-3"><Button><Heart data-icon="inline-start" />Save car</Button><Button variant="outline" render={<a href={car.sourceUrl} target="_blank" rel="noreferrer" />} nativeButton={false}>View original listing<ExternalLink data-icon="inline-end" /></Button></div><p className="mt-4 text-xs text-muted-foreground">Illustrative listing only. Verify price and availability with the source.</p></div></div>
}
