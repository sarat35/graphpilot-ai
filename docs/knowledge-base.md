# BuySeconds — Knowledge Base

## Product purpose

BuySeconds helps Indian used-car customers turn a set of preferences into a short, source-linked shortlist. The customer signs in, chooses a city and optional vehicle preferences, and receives up to five relevant marketplace links rather than having to sift through broad web-search pages.

The product’s promise is **“Describe what you need; inspect the best available matches.”** A result must always link to its original source and must not be presented as an independently verified fact when it came only from a search snippet.

## Customers and core journey

- **Walk-in guest:** can view public pages and sign in or sign up.
- **Authenticated customer:** can search, view results, save supported vehicles, and use the chatbot.

1. The customer signs in with Supabase Auth.
2. In the guided Search wizard, they select a required city and optional budget, brand, **model**, fuel type, maximum age, and maximum kilometres.
3. They review the criteria and choose **Compare top matches**.
4. The app calls the authenticated FastAPI API. The search workflow queries Google Serper, rejects generic category pages where possible, ranks city-relevant marketplace links, and returns no more than five results.
5. The customer can open a source link directly, edit the search, reuse a recent search, or continue through the chatbot.

## Product rules

- City is required. Brand, model, budget, fuel, age, and kilometres are optional preferences.
- Model is a free-text vehicle-model preference, for example `Nexon EV`, `Swift`, or `City`.
- Results are capped at five. A live search may return fewer than five when sufficiently specific marketplace listings are unavailable.
- The app must show source links and must not invent price, year, kilometres, availability, or a “value for money” claim that cannot be supported by the source data.
- Google Serper is used for discovery only. The application does not scrape marketplaces.
- Direct marketplace APIs or licensed feeds are required before the application can guarantee five complete, verified vehicle records for every search.
- Customers may access only their own searches, saved vehicles, and conversations.

## Current implementation

| Area | Current behaviour |
| --- | --- |
| Web Counter | Next.js App Router with protected Search, Results, Products, Chatbot, and Account pages. |
| ID Check | Supabase email/password authentication; protected routes and FastAPI JWT/JWKS verification. |
| Search Clerk | Async FastAPI endpoints with Pydantic request/response validation and request IDs. |
| Live discovery | LangGraph search workflow using Google Serper, with city/brand/model/fuel/query ranking and source links. |
| Chat | LangGraph conversation workflow retains the current conversation in the browser/API-process session and extracts city/fuel preferences. |
| Warehouse | Supabase migrations and Row Level Security are applied, including `searches.model` and `external_search_results`. |
| Persistence gap | Active search, saved-vehicle, and conversation repositories are in-memory. They reset when the API restarts; wiring them to Supabase is the next delivery block. |

## Architecture boundaries

- `apps/web` is the **Counter**: presentation, form state, authentication session, navigation, and user feedback.
- `apps/api` is the **Clerk**: authentication validation, input validation, search orchestration, and owner checks.
- Supabase Auth is the **ID Check**.
- Supabase Postgres is the future durable **Warehouse** for private customer records and verified inventory.
- LangGraph workflows are the **Back Room Specialists** for structured search and conversation handling.
- Google Serper is an **External Vendor** used only by the Clerk.

See [architecture-design.md](architecture-design.md) for the detailed data flow, security rules, and staged production architecture.

## Engineering principles

1. Keep browser code free of server secrets. Only `NEXT_PUBLIC_*` Supabase values belong in the web application environment.
2. Validate every API request with Pydantic; do not trust criteria from the browser.
3. Keep provider calls asynchronous, time-bounded, structured, and behind FastAPI services.
4. Use exact ownership checks today and Supabase RLS as the durable Warehouse guard.
5. Preserve loading, empty, and error states; a failed provider call must not leave the customer on an infinite loading screen.
6. Use tests with mock search mode for deterministic API behaviour. Live Serper calls are an integration concern, not a unit-test dependency.
7. Never scrape sources or store secrets, tokens, or raw credentials in customer records or logs.

## Configuration and operation

- Root `.env` contains server-side search, Supabase, and Supabase CLI configuration.
- `apps/web/.env.local` contains only `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
- `PRODUCT_SEARCH_MODE=live` enables Google Serper. `mock` enables deterministic listings for development and automated tests.
- Apply schema changes with `npx supabase db push` after reviewing migrations in `supabase/migrations`.

## Success measures

- Authenticated search completion rate.
- Rate of source-link opens from ranked results.
- Saved-car intent and successful save rate.
- Zero-result rate, provider error rate, and search latency.
- Chat-to-search completion rate.
- Once persistence is connected: returning-customer search and conversation recovery after an API restart.

## Next required delivery

Replace the in-memory repositories with Supabase/Postgres repositories. Persist each member search and its selected `external_search_results`, then persist saved vehicles and conversation messages. This makes customer history durable and enables reliable ownership/RLS integration tests.

## Reusable application-development checklist

Use this sequence as a high-level guide for future applications. Repeat the Test-Driven Development loop for each bounded feature: write a failing test, implement the smallest correct behaviour, then refactor while the tests stay green.

1. **Define the product requirement.** Write the problem, target customers, goals, non-goals, success measures, and acceptance criteria.
2. **Create the frontend PRD and UI prototype.** Define routes, user flows, responsive states, accessibility expectations, loading/empty/error states, and mock data.
3. **Create a knowledge base.** Record business vocabulary, decisions, constraints, external dependencies, security rules, and unresolved questions.
4. **Design the architecture.** Define frontend, API, authentication, database, AI/integration, data-flow, ownership, and operational boundaries before implementation expands.
5. **Set up source control and environments.** Create `.env.example`, protect secrets, separate browser-safe and server-only configuration, and document local setup.
6. **Design and migrate the database.** Define schemas, relationships, indexes, migrations, ownership rules, Row Level Security where applicable, and a rollback/recovery approach.
7. **Implement identity and authorization.** Validate sign-up, sign-in, session refresh, protected routes, token verification, and “customer A cannot access customer B’s data” tests.
8. **Implement feature slices with TDD.** Build the UI, API contract, validation, service, repository, and tests together for one user flow at a time.
9. **Validate complete flows with mocks.** Exercise happy paths plus validation, empty, error, timeout, and recovery paths before enabling paid or external services.
10. **Enable live integrations safely.** Add timeouts, structured validation, source attribution, rate limits, retries where appropriate, and no-secret logging. Verify the real provider with controlled test cases.
11. **Persist and verify real data.** Replace temporary repositories, test migrations against a non-production environment, prove ownership/RLS, and confirm data survives restarts.
12. **Prepare for release.** Run automated tests, type/lint checks, accessibility and responsive checks, security review, performance checks, backups, monitoring, alerts, deployment, and rollback validation.
13. **Operate and improve.** Track product metrics, errors, latency, provider cost/availability, customer feedback, and update the PRD, knowledge base, and architecture when decisions change.
