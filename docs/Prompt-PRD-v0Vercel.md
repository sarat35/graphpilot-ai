# BuySeconds — Product Requirements Document

## 1. Product summary

BuySeconds is an authenticated used-car discovery experience for India. It helps a customer specify what they want and then presents up to five city-relevant, ranked marketplace links with direct source access.

The product should reduce broad, unstructured browsing. It must be transparent about the source of each listing and must never fabricate vehicle data.

## 2. Goals and non-goals

### Goals

- Let a signed-in customer search by city, budget, brand, **vehicle model**, fuel type, age, and kilometres.
- Provide up to five ranked, city-specific marketplace results with source links.
- Preserve the current chatbot conversation during the browser session and use recognised preferences to run a search.
- Protect customer-specific resources using Supabase Auth and FastAPI token validation.
- Prepare all private customer data for durable Supabase/Postgres storage with Row Level Security.

### Non-goals

- Do not scrape marketplace websites.
- Do not represent Google Serper snippets as verified vehicle inventory.
- Do not promise exactly five listings when the live provider cannot return five sufficiently relevant direct listings.
- Do not expose Google Serper, Supabase secret, database, or Supabase CLI credentials to the browser.
- Do not add payments, dealer administration, or an unapproved inventory-management interface.

## 3. Technology requirements

| Layer | Required technology |
| --- | --- |
| Customer interface | Next.js App Router, React, TypeScript, Tailwind CSS, shadcn/Base UI, Lucide icons |
| Authentication | Supabase Auth email/password with browser sessions |
| API | Asynchronous Python FastAPI, versioned under `/api/v1` |
| Validation | Pydantic request and response models |
| Search orchestration | LangGraph workflows and Google Serper through server-side tools |
| Warehouse | Supabase Postgres, migrations, Row Level Security |

## 4. Required routes

| Route | Requirement |
| --- | --- |
| `/` | Public landing page. |
| `/auth/signin` and `/auth/signup` | Supabase email/password authentication. |
| `/search` | Protected guided search wizard. |
| `/results?searchId=…` | Protected ranked-results page for the member’s search. |
| `/product/[id]` | Protected product detail view when an internal vehicle record exists. |
| `/products` | Protected saved-products page. |
| `/chatbot` | Protected conversation and guided-discovery page. |
| `/account` | Protected account page. |

Protected pages use the shared authenticated layout, desktop navigation, responsive mobile navigation, and the chatbot launcher.

## 5. Guided-search requirements

The wizard contains these stages:

1. City — required.
2. Minimum/maximum budget — optional.
3. Brand — optional selectable preference.
4. **Model — optional free-text vehicle model, displayed directly below Brand.**
5. Fuel type — optional single selection.
6. Maximum vehicle age — optional.
7. Maximum kilometres driven — optional.
8. Review and submit.

The review page shows every selected criterion, including Model. Recent-search labels include brand/model where supplied. On submit, the Counter sends the structured request to `POST /api/v1/searches` with the authenticated Supabase access token.

## 6. Live-search requirements

1. FastAPI validates all criteria using Pydantic.
2. The LangGraph search workflow builds a city-specific query using supplied brand, model, fuel, budget, age, and kilometres.
3. Google Serper is called asynchronously by a server-side integration.
4. The workflow filters/ranks candidate marketplace links, prioritising city, brand, model, fuel, price, year, and kilometre evidence found in source snippets.
5. The response contains no more than five structured results: title, snippet, source name, source URL, and any safely parsed vehicle fields.
6. The Results page clearly shows rank and a **View source** link that opens in a new tab.
7. If no relevant links are available, show a clear empty state with an option to edit the search. Do not keep the page loading indefinitely.
8. Provider errors return a clear recoverable API/UI error; they must not expose keys or internal stack traces.

## 7. Chatbot requirements

- Create and resume the active conversation for the current browser session.
- Keep messages in order and show user and assistant messages distinctly.
- Extract recognised city and fuel preferences into structured conversation criteria.
- When enough criteria are available, invoke the same product-search service and return source-linked results.
- Do not claim that an AI model verified vehicle facts. Preserve missing/ambiguous criteria as questions or uncertainty.

## 8. Data, security, and persistence requirements

- Supabase migrations define `profiles`, `vehicles`, `searches`, `search_results`, `external_search_results`, `saved_vehicles`, `conversations`, and related supporting shelves.
- `searches` includes `model` as an optional value.
- RLS must prevent a customer from reading or writing another customer’s private records.
- FastAPI must verify the Supabase JWT before accessing a member-specific resource.
- Current in-memory repositories are temporary. Replace them with Supabase/Postgres repositories so searches, saved vehicles, and conversations survive API restarts.
- Persist selected external search results with their source URL and raw provider payload only after appropriate redaction and retention decisions.

## 9. Acceptance criteria

- A signed-in customer can enter `Tata`, `Nexon EV`, `Electric`, and `Hyderabad`; Model appears under Brand in the wizard and on the review screen.
- The API receives and validates `model`, includes it in the live query, and gives matching listings higher rank.
- A successful results response contains at most five source-linked items; it may contain fewer when fewer relevant direct listings exist.
- The Results UI shows an accessible loading state, result cards, explicit source links, an empty state, and a recoverable error state.
- A customer cannot retrieve another customer’s search, saved vehicle, or conversation through the API.
- The API health endpoint responds successfully when the service is running.
- Backend tests use mock search mode; frontend type checking passes.
- No secret configuration appears in browser-delivered code, logs, screenshots, or documentation examples.

## 10. Delivery priorities

1. **Durable customer records:** replace in-memory search, saved-vehicle, and conversation repositories with Supabase/Postgres implementations.
2. **Trusted inventory:** integrate approved marketplace APIs or feeds, normalize vehicle fields, and use Warehouse inventory for exact filtering.
3. **Operational quality:** add rate limits, provider observability, database-backed RLS tests, performance monitoring, and recovery procedures.

See [knowledge-base.md](knowledge-base.md) for product context and [architecture-design.md](architecture-design.md) for the architecture and implementation status.
