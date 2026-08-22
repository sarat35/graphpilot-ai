import type { Metadata } from "next"
import Link from "next/link"
import { PublicOnlyGuard } from "@/components/auth/public-only-guard"
import { AuthLayout } from "@/components/auth/auth-layout"
import { SignUpForm } from "@/components/auth/sign-up-form"

export const metadata: Metadata = {
  title: "Sign Up — BuySeconds",
  description: "Create a BuySeconds account to search, compare, and save used car matches.",
}

export default function SignUpPage() {
  return (
    <PublicOnlyGuard>
      <AuthLayout
        title="Create your account"
        description="Tell us who you are so we can save your searches and matches."
        footer={
          <>
            Already have an account?{" "}
            <Link href="/auth/signin" className="font-medium text-foreground underline-offset-4 hover:underline">
              Sign in
            </Link>
          </>
        }
      >
        <SignUpForm />
      </AuthLayout>
    </PublicOnlyGuard>
  )
}
