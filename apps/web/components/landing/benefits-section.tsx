import { Gauge, ListChecks, ShieldCheck, Bookmark } from "lucide-react"

const BENEFITS = [
  {
    icon: Gauge,
    title: "Faster than manual browsing",
    description: "One guided search replaces scrolling across several marketplace tabs.",
  },
  {
    icon: ListChecks,
    title: "Ranked, not just listed",
    description: "Every result carries a match percentage and the specific reasons behind it.",
  },
  {
    icon: Bookmark,
    title: "A shortlist that sticks",
    description: "Save up to five cars and revisit your five most recent searches anytime.",
  },
  {
    icon: ShieldCheck,
    title: "Transparent by design",
    description: "Listings link back to their original source so you can verify before you buy.",
  },
]

export function BenefitsSection() {
  return (
    <section className="border-y border-border bg-secondary/40">
      <div className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-8 px-4 py-16 sm:grid-cols-2 sm:px-6 sm:py-20 lg:grid-cols-4">
        {BENEFITS.map((benefit) => {
          const Icon = benefit.icon
          return (
            <div key={benefit.title} className="flex flex-col gap-3">
              <div className="flex size-10 items-center justify-center rounded-md bg-primary/15 text-primary">
                <Icon className="size-5" aria-hidden="true" />
              </div>
              <h3 className="font-heading text-lg font-semibold">{benefit.title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {benefit.description}
              </p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
