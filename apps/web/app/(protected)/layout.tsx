import { ProtectedGuard } from "@/components/auth/protected-guard"
import { AuthenticatedShell } from "@/components/layout/authenticated-shell"

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedGuard>
      <AuthenticatedShell>{children}</AuthenticatedShell>
    </ProtectedGuard>
  )
}
