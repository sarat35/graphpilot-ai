import type { Metadata } from "next"
import { SearchWizard } from "@/components/search/search-wizard"

export const metadata: Metadata = {
  title: "Search — BuySeconds",
  description: "Answer a few questions and BuySeconds will compare the five best used car matches for you.",
}

export default function SearchPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 sm:py-10">
      <SearchWizard />
    </div>
  )
}
