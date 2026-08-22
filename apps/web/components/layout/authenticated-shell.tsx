"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { MessageCircle, LogOut, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/lib/auth-context"
import { BrandMark } from "@/components/brand-mark"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { AUTHENTICATED_NAV_ITEMS } from "@/components/layout/nav-config"

function initialsFor(name: string) {
  return name
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase()
}

function isActivePath(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`)
}

function DesktopSidebar() {
  const pathname = usePathname()
  const { session, signOut } = useAuth()

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground md:flex">
      <div className="flex h-16 items-center px-5">
        <Link href="/search" aria-label="BuySeconds home">
          <BrandMark
            wordmarkClassName="text-sidebar-foreground"
            markClassName="bg-sidebar-primary text-sidebar-primary-foreground"
          />
        </Link>
      </div>
      <nav aria-label="Primary" className="flex flex-1 flex-col gap-1 px-3 py-2">
        {AUTHENTICATED_NAV_ITEMS.map((item) => {
          const active = isActivePath(pathname, item.href)
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground"
              )}
            >
              <Icon className="size-4 shrink-0" aria-hidden="true" />
              {item.label}
            </Link>
          )
        })}
      </nav>
      <div className="border-t border-sidebar-border p-3">
        {session && (
          <div className="mb-2 flex items-center gap-2.5 rounded-md px-2 py-1.5">
            <Avatar className="size-8">
              <AvatarFallback className="bg-sidebar-accent text-xs text-sidebar-accent-foreground">
                {initialsFor(session.name)}
              </AvatarFallback>
            </Avatar>
            <div className="flex min-w-0 flex-col">
              <span className="truncate text-sm font-medium text-sidebar-foreground">
                {session.name}
              </span>
              <span className="truncate text-xs text-sidebar-foreground/60">
                {session.email}
              </span>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground"
          onClick={signOut}
          render={<Link href="/" />}
          nativeButton={false}
        >
          <LogOut data-icon="inline-start" />
          Sign Out
        </Button>
      </div>
    </aside>
  )
}

function MobileBottomNav() {
  const pathname = usePathname()

  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-4 border-t border-sidebar-border bg-sidebar text-sidebar-foreground md:hidden"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      {AUTHENTICATED_NAV_ITEMS.map((item) => {
        const active = isActivePath(pathname, item.href)
        const Icon = item.icon
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex flex-col items-center gap-1 py-2.5 text-[0.7rem] font-medium",
              active ? "text-sidebar-primary" : "text-sidebar-foreground/60"
            )}
          >
            <Icon className="size-5" aria-hidden="true" />
            {item.label}
          </Link>
        )
      })}
    </nav>
  )
}

function ChatbotLauncher() {
  const pathname = usePathname()
  const [open, setOpen] = React.useState(false)

  if (pathname === "/chatbot") return null

  return (
    <div className="fixed right-4 bottom-20 z-40 md:right-6 md:bottom-6">
      {open && (
        <div className="mb-3 w-72 rounded-lg border border-border bg-popover p-4 text-sm text-popover-foreground shadow-lg sm:w-80">
          <div className="mb-2 flex items-center justify-between">
            <p className="font-heading text-sm font-semibold">Find a car by chat</p>
            <Button
              variant="ghost"
              size="icon-xs"
              onClick={() => setOpen(false)}
              aria-label="Close chat preview"
            >
              <X />
            </Button>
          </div>
          <p className="text-muted-foreground">
            The guided chat assistant is coming in a later build step. Open the full{" "}
            <Link href="/chatbot" className="text-primary underline underline-offset-4">
              Chatbot page
            </Link>{" "}
            once it&apos;s available.
          </p>
        </div>
      )}
      <Button
        size="icon-lg"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close chatbot" : "Open chatbot"}
        className="rounded-full shadow-lg"
      >
        <MessageCircle />
      </Button>
    </div>
  )
}

export function AuthenticatedShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-svh bg-background">
      <DesktopSidebar />
      <MobileBottomNav />
      <ChatbotLauncher />
      <main className="min-h-svh pb-20 md:ml-64 md:pb-0">{children}</main>
    </div>
  )
}
