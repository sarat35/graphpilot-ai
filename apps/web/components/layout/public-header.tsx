import Link from "next/link"
import { BrandMark } from "@/components/brand-mark"
import { Button } from "@/components/ui/button"

export function PublicHeader() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center" aria-label="BuySeconds home">
          <BrandMark />
        </Link>
        <nav className="flex items-center gap-2" aria-label="Account actions">
          <Button
            variant="ghost"
            size="sm"
            render={<Link href="/auth/signin" />}
            nativeButton={false}
          >
            Sign In
          </Button>
          <Button size="sm" render={<Link href="/auth/signup" />} nativeButton={false}>
            Sign Up
          </Button>
        </nav>
      </div>
    </header>
  )
}
