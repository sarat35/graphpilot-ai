"use client"

import * as React from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { AlertCircle } from "lucide-react"
import { useAuth } from "@/lib/auth-context"
import { Field, FieldGroup, FieldLabel, FieldError } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Spinner } from "@/components/ui/spinner"

function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}

export function SignInForm() {
  const { signIn } = useAuth()
  const router = useRouter()
  const searchParams = useSearchParams()

  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [emailTouched, setEmailTouched] = React.useState(false)
  const [passwordTouched, setPasswordTouched] = React.useState(false)
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [formError, setFormError] = React.useState<string | null>(null)

  const emailError =
    emailTouched && !isValidEmail(email) ? "Enter a valid email" : undefined
  const passwordError =
    passwordTouched && password.length === 0 ? "Password is required" : undefined

  const canSubmit = isValidEmail(email) && password.length > 0 && !isSubmitting

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setEmailTouched(true)
    setPasswordTouched(true)
    setFormError(null)

    if (!isValidEmail(email) || password.length === 0) return

    setIsSubmitting(true)
    try {
      await signIn({ email, password })
      const from = searchParams.get("from")
      router.replace(from && from.startsWith("/") ? from : "/search")
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Something went wrong. Please try again.")
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <FieldGroup>
        {formError && (
          <Alert variant="destructive">
            <AlertCircle />
            <AlertTitle>Couldn&apos;t sign in</AlertTitle>
            <AlertDescription>{formError}</AlertDescription>
          </Alert>
        )}
        <Field data-invalid={!!emailError}>
          <FieldLabel htmlFor="signin-email">Email</FieldLabel>
          <Input
            id="signin-email"
            type="email"
            autoComplete="email"
            value={email}
            aria-invalid={!!emailError}
            onChange={(event) => setEmail(event.target.value)}
            onBlur={() => setEmailTouched(true)}
            placeholder="you@example.com"
          />
          <FieldError>{emailError}</FieldError>
        </Field>
        <Field data-invalid={!!passwordError}>
          <FieldLabel htmlFor="signin-password">Password</FieldLabel>
          <Input
            id="signin-password"
            type="password"
            autoComplete="current-password"
            value={password}
            aria-invalid={!!passwordError}
            onChange={(event) => setPassword(event.target.value)}
            onBlur={() => setPasswordTouched(true)}
            placeholder="Your password"
          />
          <FieldError>{passwordError}</FieldError>
        </Field>
        <Button type="submit" disabled={!canSubmit} className="mt-1 h-10 w-full">
          {isSubmitting ? (
            <>
              <Spinner data-icon="inline-start" />
              Signing in…
            </>
          ) : (
            "Sign In"
          )}
        </Button>
      </FieldGroup>
    </form>
  )
}
