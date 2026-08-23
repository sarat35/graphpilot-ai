import nextEnv from "@next/env"
import path from "node:path"

// The monorepo keeps its local secrets at the repository root. Load them
// before Next.js captures public variables for the browser bundle.
const { loadEnvConfig } = nextEnv
loadEnvConfig(path.resolve(process.cwd(), "../.."))
/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
}

export default nextConfig
