"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function AccountPage() {
  const { session, signOut } = useAuth()
  const [city, setCity] = useState("Bengaluru")
  const [saved, setSaved] = useState(false)
  return <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 sm:py-10"><p className="text-sm font-medium text-primary">Account</p><h1 className="font-heading text-2xl font-semibold">Your preferences</h1><section className="mt-6 rounded-xl border bg-card p-6"><h2 className="font-heading text-lg font-semibold">Profile</h2><p className="mt-2 text-sm">{session?.name}</p><p className="text-sm text-muted-foreground">{session?.email}</p></section><section className="mt-4 rounded-xl border bg-card p-6"><label className="text-sm font-medium" htmlFor="default-city">Default search city</label><div className="mt-3 flex max-w-md gap-2"><Input id="default-city" value={city} onChange={(event) => { setCity(event.target.value); setSaved(false) }} /><Button onClick={() => setSaved(true)}>Save</Button></div>{saved && <p className="mt-3 text-sm text-emerald-700">Preferences saved for this browser session.</p>}</section><section className="mt-4 rounded-xl border border-destructive/30 bg-card p-6"><h2 className="font-heading text-lg font-semibold">Session</h2><p className="mt-1 text-sm text-muted-foreground">Signing out clears the demo session and saved cars on this browser.</p><Button variant="destructive" className="mt-4" onClick={signOut}>Sign out</Button></section></div>
}
