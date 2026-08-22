import { BrandMark } from "@/components/brand-mark"

const FOOTER_LINKS = ["How It Works", "For Sellers", "Support", "Privacy"]

export function PublicFooter() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6">
        <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
          <BrandMark />
          <nav aria-label="Footer" className="flex flex-wrap gap-x-6 gap-y-2">
            {FOOTER_LINKS.map((link) => (
              <span
                key={link}
                className="cursor-default text-sm text-muted-foreground"
                aria-disabled="true"
                title="Placeholder link — not functional in this prototype"
              >
                {link}
              </span>
            ))}
          </nav>
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          BuySeconds is a product-discovery prototype. All listings, prices, and marketplace
          names shown are demonstration data and do not reflect real, currently available
          vehicles.
        </p>
      </div>
    </footer>
  )
}
