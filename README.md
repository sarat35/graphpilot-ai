# BuySeconds

BuySeconds is a used-car discovery application. A signed-in customer can describe the car they want, search current marketplace listings, receive up to five ranked matches with source links, save cars, and continue the conversation through the chatbot.

## What it does

- Provides Supabase email/password sign-up and sign-in.
- Collects city, budget, brand, **model**, fuel type, maximum age, and maximum kilometres in a guided Next.js search flow.
- Uses FastAPI, LangGraph, Pydantic validation, and Google Serper to fetch and rank city-specific marketplace listings.
- Returns a maximum of five matches and links customers directly to the source listing.
- Keeps chat conversation context for the browser session.
- Includes Supabase migrations for the application database, ownership rules, and external search-result storage.

## Project layout

| Path | Purpose |
| --- | --- |
| `apps/web` | Next.js customer web application |
| `apps/api` | FastAPI service, LangGraph workflows, search integration, and API tests |
| `supabase` | Supabase configuration and database migrations |
| `docs` | Product knowledge base, API contract, and architecture design |

## Prerequisites

- Node.js 20 or later
- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- A Supabase project with email/password authentication enabled
- A [Google Serper](https://serper.dev/) API key for live product search
- The Supabase CLI for applying database migrations

## Configure the application

1. Create the server configuration file from the example:

   ```sh
   cp .env.example .env
   ```

2. In the root `.env`, set the values required by the API:

   ```dotenv
   PRODUCT_SEARCH_MODE=live
   GOOGLE_SERPER_API_KEY=...
   INTELLIGENCE_MODEL_NAME=...
   SUPABASE_URL=https://<project-ref>.supabase.co
   SUPABASE_PUBLISHABLE_KEY=...
   SUPABASE_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json
   ```

   `SUPABASE_JWKS_URL` is optional when `SUPABASE_URL` is set. The API derives it automatically.

3. Create `apps/web/.env.local` with only browser-safe values:

   ```dotenv
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
   NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=...
   ```

   Never put Google Serper, Supabase secret, database, or Supabase CLI credentials in `.env.local`.

## Set up Supabase

Log in to the Supabase CLI, link the project, then apply the database schema:

```sh
npx supabase login
npx supabase link --project-ref <project-ref>
npx supabase db push
```

The migrations create the user profiles, vehicles, saved vehicles, searches, conversations, external search-result storage, indexes, and Row Level Security policies. See [supabase/README.md](supabase/README.md) for more detail.

## Install dependencies

From the repository root:

```sh
make api-sync
make web-install
```

## Run locally

Start the API in one terminal:

```sh
make api-run
```

The API is available at <http://localhost:8000>, with interactive documentation at <http://localhost:8000/docs>.

Start the web app in a second terminal:

```sh
make web-dev
```

Open <http://localhost:3000> and create an account before running a search.

## Test and validate

Run all backend tests:

```sh
make api-test
```

Run backend formatting and lint checks:

```sh
make api-check
```

Run the frontend type check:

```sh
cd apps/web
./node_modules/.bin/tsc --noEmit
```

## Search modes

`PRODUCT_SEARCH_MODE` controls product-search behaviour:

- `live` — calls Google Serper and ranks marketplace results.
- `mock` — returns deterministic sample listings for development and automated tests.

Use `mock` when developing without a Serper key. Automated tests set this mode where they need deterministic results.

## Useful API endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Confirm the API is running |
| `POST /api/v1/searches` | Create an authenticated car search |
| `GET /api/v1/searches/{search_id}/results` | Retrieve ranked source-linked matches |
| `GET /api/v1/saved-vehicles` | List saved cars |
| `POST /api/v1/conversations` | Start a chat session |

## Troubleshooting

- **“Failed to fetch” in the web app:** Start the API with `make api-run`, then confirm <http://localhost:8000/health> returns a successful response.
- **Authentication errors:** Check that the browser public Supabase URL/key match the API `SUPABASE_URL` and that Supabase email/password authentication is enabled.
- **No live results:** Confirm `PRODUCT_SEARCH_MODE=live`, the Serper key is configured, and use a city and criteria likely to have active listings.
- **Database migration fails:** Re-run `npx supabase link --project-ref <project-ref>` and ensure the Supabase CLI credentials in the root `.env` are valid.

## Additional documentation

- [Architecture design](docs/architecture-design.md)
- [Knowledge base](docs/knowledge-base.md)
- [API contract](docs/api-contract.md)
- [Supabase database guide](supabase/README.md)
