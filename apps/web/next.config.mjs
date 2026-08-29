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
  async rewrites() {
    const apiUpstream = process.env.API_UPSTREAM_URL ?? "http://127.0.0.1:8000"
    return [
      {
        source: "/backend-api/:path*",
        destination: `${apiUpstream}/api/v1/:path*`,
      },
    ]
  },
}

export default nextConfig
