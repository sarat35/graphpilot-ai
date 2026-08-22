import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

export function FinalCtaSection() {
  return (
    <section className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 sm:py-20">
      <div className="flex flex-col items-start justify-between gap-6 rounded-xl bg-primary px-6 py-10 text-primary-foreground sm:flex-row sm:items-center sm:px-10">
        <div className="max-w-lg">
          <h2 className="font-heading text-2xl font-semibold tracking-tight sm:text-3xl">
            Ready to find your next car?
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-primary-foreground/80 sm:text-base">
            Create a free demo account and run your first guided search in under a minute.
          </p>
        </div>
        <Button
          size="lg"
          variant="secondary"
          className="h-11 shrink-0 px-6"
          render={<Link href="/auth/signup" />}
          nativeButton={false}
        >
          Sign Up Free
          <ArrowRight data-icon="inline-end" />
        </Button>
      </div>
    </section>
  )
}
