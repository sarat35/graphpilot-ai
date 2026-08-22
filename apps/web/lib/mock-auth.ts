import { MOCK_USERS } from "./mock-data"
import type { Session } from "./types"
import { simulateDelay } from "./storage"

// Simulated authentication service. No real credential storage or network
// requests occur here — this exists purely to prototype front-end flows.

export class AuthError extends Error {}
export class NetworkError extends Error {}

interface SignInInput {
  email: string
  password: string
}

interface SignUpInput {
  name: string
  email: string
  password: string
}

function normalizeEmail(email: string) {
  return email.trim().toLowerCase()
}

// Deterministic fixture: entering this email simulates a dropped connection
// instead of a real credential check, so the offline state can be reviewed
// without relying on an actual network condition.
const OFFLINE_DEMO_EMAIL = "offline@buyseconds.com"

export async function mockSignIn({ email, password }: SignInInput): Promise<Session> {
  await simulateDelay(900)

  if (normalizeEmail(email) === OFFLINE_DEMO_EMAIL) {
    throw new NetworkError("Check your internet connection")
  }

  const user = MOCK_USERS.find((candidate) => normalizeEmail(candidate.email) === normalizeEmail(email))

  if (!user || user.password !== password) {
    throw new AuthError("Invalid email or password")
  }

  return { userId: user.id, name: user.name, email: user.email }
}

export async function mockSignUp({ name, email, password }: SignUpInput): Promise<Session> {
  await simulateDelay(1100)

  if (normalizeEmail(email) === OFFLINE_DEMO_EMAIL) {
    throw new NetworkError("Check your internet connection")
  }

  const existing = MOCK_USERS.find((candidate) => normalizeEmail(candidate.email) === normalizeEmail(email))

  if (existing) {
    throw new AuthError("An account with that email already exists")
  }

  // Prototype accounts are created in-memory for the session only; they are
  // not persisted to any real user store.
  const id = `user-${Math.random().toString(36).slice(2, 8)}`
  return { userId: id, name, email }
}
