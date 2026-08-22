import type { Metadata } from "next"
import { PublicOnlyGuard } from "@/components/auth/public-only-guard"
import { PublicHeader } from "@/components/layout/public-header"
import { PublicFooter } from "@/components/layout/public-footer"
import { HeroSection } from "@/components/landing/hero-section"
import { HowItWorksSection } from "@/components/landing/how-it-works-section"
import { BenefitsSection } from "@/components/landing/benefits-section"
import { FinalCtaSection } from "@/components/landing/final-cta-section"

export const metadata: Metadata = {
  title: "BuySeconds — Compare the five best used car matches",
  description:
    "Describe the used car you want and BuySeconds ranks the five best demo matches with a plain-language explanation for each.",
}

export default function LandingPage() {
  return (
    <PublicOnlyGuard>
      <div className="flex min-h-svh flex-col">
        <PublicHeader />
        <main className="flex-1">
          <HeroSection />
          <HowItWorksSection />
          <BenefitsSection />
          <FinalCtaSection />
        </main>
        <PublicFooter />
      </div>
    </PublicOnlyGuard>
  )
}
