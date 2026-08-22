"use client"

import { HistoryIcon, XIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Empty, EmptyHeader, EmptyMedia, EmptyTitle, EmptyDescription } from "@/components/ui/empty"
import type { RecentSearch } from "@/lib/types"

export function RecentSearchesPanel({
  searches,
  onApply,
  onRemove,
}: {
  searches: RecentSearch[]
  onApply: (search: RecentSearch) => void
  onRemove: (id: string) => void
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h2 className="mb-3 font-heading text-sm font-semibold">Recent searches</h2>
      {searches.length === 0 ? (
        <Empty className="py-6">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <HistoryIcon />
            </EmptyMedia>
            <EmptyTitle className="text-sm">No searches yet</EmptyTitle>
            <EmptyDescription>Your last five searches will show up here.</EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : (
        <ul className="flex flex-col gap-1">
          {searches.map((search) => (
            <li key={search.id} className="group flex items-center gap-1 rounded-md">
              <Button
                type="button"
                variant="ghost"
                onClick={() => onApply(search)}
                className="h-auto flex-1 justify-start whitespace-normal px-2 py-2 text-left text-sm font-normal text-foreground"
              >
                {search.label}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-xs"
                aria-label={`Remove search: ${search.label}`}
                className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
                onClick={() => onRemove(search.id)}
              >
                <XIcon />
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
