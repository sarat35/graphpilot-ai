"use client"

import { useState, type FormEvent } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { EyeIcon, EyeOffIcon, AlertCircleIcon, WifiOffIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel, FieldDescription, FieldError } from "@/components/ui/field"
import { InputGroup, InputGroupInput, InputGroupAddon, InputGroupButton } from "@/components/ui/input-group"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Spinner } from "@/components/ui/spinner"
import { useAuth, AuthError, NetworkError } from "@/lib/auth-context"

export function SignUpForm() {
  const router = useRouter()
  const { signUp } = useAuth()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorKind, setErrorKind] = useState<"credentials" | "network" | null>(null)
  const [errorMessage, setErrorMessage] = useState("")
  const [fieldError, setFieldError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorKind(null)
    setFieldError(null)

    if (password.length < 8) {
      setFieldError("Password must be at least 8 characters")
      return
    }

    setIsSubmitting(true)
    try {
      await signUp({ name, email, password })
      router.push("/search")
    } catch (error) {
      if (error instanceof NetworkError) {
        setErrorKind("network")
        setErrorMessage(error.message)
      } else if (error instanceof AuthError) {
        setErrorKind("credentials")
        setErrorMessage(error.message)
      } else {
        setErrorKind("credentials")
        setErrorMessage("Something went wrong. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {errorKind && (
        <Alert variant="destructive">
          {errorKind === "network" ? (
            <WifiOffIcon data-icon="inline-start" />
          ) : (
            <AlertCircleIcon data-icon="inline-start" />
          )}
          <AlertTitle>{errorKind === "network" ? "You're offline" : "Couldn't create account"}</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="name">Full name</FieldLabel>
          <InputGroup>
            <InputGroupInput
              id="name"
              type="text"
              autoComplete="name"
              placeholder="Jordan Lee"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </InputGroup>
        </Field>

        <Field>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <InputGroup>
            <InputGroupInput
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </InputGroup>
        </Field>

        <Field data-invalid={fieldError ? true : undefined}>
          <FieldLabel htmlFor="password">Password</FieldLabel>
          <InputGroup>
            <InputGroupInput
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              aria-invalid={fieldError ? true : undefined}
              required
              minLength={8}
            />
            <InputGroupAddon align="inline-end">
              <InputGroupButton
                type="button"
                size="icon-xs"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((v) => !v)}
              >
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
              </InputGroupButton>
            </InputGroupAddon>
          </InputGroup>
          {fieldError ? (
            <FieldError>{fieldError}</FieldError>
          ) : (
            <FieldDescription>Use 8 or more characters with a mix of letters and numbers.</FieldDescription>
          )}
        </Field>
      </FieldGroup>

      <Button type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? <Spinner data-icon="inline-start" /> : null}
        {isSubmitting ? "Creating account..." : "Create account"}
      </Button>
    </form>
  )
}
