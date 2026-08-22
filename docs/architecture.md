# Architecture

BuySeconds is organized as a monorepo with independently deployable applications:

- `apps/web` contains the Next.js frontend.
- `apps/api` contains the Python API service.
- `packages/api-client` will hold the shared frontend client generated from the API contract.

The frontend communicates with the API only through the versioned API contract. Marketplace integrations and business services remain owned by the API.
