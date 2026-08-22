import type { Metadata } from "next"
import Link from "next/link"
import { PublicOnlyGuard } from "@/components/auth/public-only-guard"
import { AuthLayout } from "@/components/auth/auth-layout"
import { SignInForm } from "@/components/auth/sign-in-form"

export const metadata: Metadata = {
  title: "Sign In — BuySeconds",
  description: "Sign in to your BuySeconds account to search and compare used cars.",
}

export default function SignInPage() {
  return (
    <PublicOnlyGuard>
      <AuthLayout
        title="Welcome back"
        description="Sign in to pick up your search where you left off."
        footer={
          <>
            New to BuySeconds?{" "}
            <Link href="/auth/signup" className="font-medium text-foreground underline-offset-4 hover:underline">
              Create an account
            </Link>
          </>
        }
      >
        <SignInForm />
      </AuthLayout>
    </PublicOnlyGuard>
  )
}
