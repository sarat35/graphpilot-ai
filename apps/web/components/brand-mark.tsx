import { cn } from "@/lib/utils"

export function BrandMark({
  className,
  markClassName,
  wordmarkClassName,
  hideWordmark = false,
}: {
  className?: string
  markClassName?: string
  wordmarkClassName?: string
  hideWordmark?: boolean
}) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <span
        aria-hidden="true"
        className={cn(
          "flex size-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground",
          markClassName
        )}
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          className="size-4"
          strokeWidth={2.2}
          stroke="currentColor"
        >
          <path
            d="M4 15.5 5.4 10a2 2 0 0 1 1.9-1.4h9.4A2 2 0 0 1 18.6 10L20 15.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M3 15.5h18v2a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="7.5" cy="17.5" r="1.25" fill="currentColor" stroke="none" />
          <circle cx="16.5" cy="17.5" r="1.25" fill="currentColor" stroke="none" />
        </svg>
      </span>
      {!hideWordmark && (
        <span
          className={cn(
            "font-heading text-lg font-semibold tracking-tight text-foreground",
            wordmarkClassName
          )}
        >
          BuySeconds
        </span>
      )}
    </span>
  )
}
