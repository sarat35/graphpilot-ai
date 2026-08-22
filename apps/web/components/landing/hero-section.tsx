import Link from "next/link"
import { ArrowRight, GaugeIcon, MapPinIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

const PREVIEW_MATCHES = [
  { rank: 1, name: "Hyundai Creta · 2020", price: "₹13.5L", city: "Mumbai", km: "41,200 km", match: 94 },
  { rank: 2, name: "Kia Seltos · 2022", price: "₹15.8L", city: "Bengaluru", km: "21,300 km", match: 88 },
  { rank: 3, name: "Tata Nexon · 2021", price: "₹8.5L", city: "Delhi", km: "32,000 km", match: 81 },
]

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-foreground text-background">
      <div className="mx-auto grid w-full max-w-6xl grid-cols-1 items-center gap-10 px-4 py-16 sm:px-6 sm:py-20 lg:grid-cols-2 lg:py-28">
        <div className="flex flex-col gap-6">
          <Badge
            variant="secondary"
            className="w-fit bg-background/10 text-background hover:bg-background/10"
          >
            Prototype · Demonstration data
          </Badge>
          <h1 className="font-heading text-4xl font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl">
            Tell us the used car you need.
            <span className="text-primary"> We&apos;ll compare the five best matches.</span>
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-background/70">
            Skip the endless scrolling across marketplaces. Answer a short guided search and
            BuySeconds ranks the five closest listings by price, age, distance, and fit — with a
            plain-language explanation for every match.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button
              size="lg"
              className="h-11 px-6"
              render={<Link href="/auth/signup" />}
              nativeButton={false}
            >
              Get Started
              <ArrowRight data-icon="inline-end" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="h-11 border-background/20 bg-transparent px-6 text-background hover:bg-background/10 hover:text-background"
              render={<Link href="/auth/signin" />}
              nativeButton={false}
            >
              Sign In
            </Button>
          </div>
        </div>
        <div
          className="relative rounded-xl border border-background/10 bg-background/5 p-4 sm:p-6"
          aria-hidden="true"
        >
          <p className="mb-4 text-xs font-medium tracking-wide text-background/50 uppercase">
            Your ranked matches
          </p>
          <div className="flex flex-col gap-3">
            {PREVIEW_MATCHES.map((car) => (
              <div
                key={car.rank}
                className="flex items-center justify-between gap-4 rounded-lg border border-background/10 bg-card px-4 py-3 text-card-foreground shadow-lg"
                style={{ opacity: 1 - (car.rank - 1) * 0.12 }}
              >
                <div className="min-w-0">
                  <p className="truncate font-heading text-sm font-semibold">{car.name}</p>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="font-medium text-foreground">{car.price}</span>
                    <span className="inline-flex items-center gap-1">
                      <MapPinIcon className="size-3" aria-hidden="true" />
                      {car.city}
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <GaugeIcon className="size-3" aria-hidden="true" />
                      {car.km}
                    </span>
                  </div>
                </div>
                <Badge
                  className={
                    car.rank === 1
                      ? "shrink-0 bg-accent text-accent-foreground"
                      : "shrink-0 bg-secondary text-secondary-foreground"
                  }
                >
                  {car.match}% match
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
