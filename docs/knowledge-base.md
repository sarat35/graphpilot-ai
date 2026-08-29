# BuySeconds — Knowledge Base

## Product purpose

BuySeconds helps authenticated used-car shoppers turn preferences into a transparent shortlist of public listings. The current release is intentionally limited to **Hyderabad**. It discovers listings from approved marketplaces, explains why each match ranked where it did, and always preserves the original source link.

The product promise is: **“Describe what you need; inspect the best available matches.”** Search discovery is not vehicle verification. Unknown source data remains unknown.

## Core journey

1. The customer signs in with Supabase Auth.
2. They choose Hyderabad and optionally enter budget, brand, model, fuel type, maximum age, and maximum kilometres.
3. FastAPI validates the request and the LangGraph workflow researches approved marketplaces.
4. The workflow collects at most 100 unique source candidates, normalizes available evidence, and ranks the best 10.
5. The customer opens source links or saves a persisted listing snapshot.
6. A saved listing is refreshed only when its owner opens it. If its source returns 404 or 410, it remains visible as `removed`.

## Product rules

- Only Hyderabad is accepted during this release.
- Approved discovery sources are Cars24, CarWale, CarTrade, Spinny, and OLX.
- The research cap is 100 unique candidates across all sources; the response cap is 10 ranked listings.
- Results must include source attribution. Google snippets are discovery evidence, not confirmed stock.
- The service must never invent vehicle price, year, mileage, city, fuel type, availability, or condition.
- Missing data receives no score credit and appears in `unmatched_or_missing_reasons`.
- A confirmed non-Hyderabad listing is excluded.
- Only the signed-in owner may read, save, refresh, or remove their records.

## Ranking policy

| Search criterion | Weight | Rule |
| --- | ---: | --- |
| City | 20% | Hyderabad must be evidenced; a known mismatch is excluded. |
| Price | 25% | The listing must fit the selected price range. |
| Brand and model | 25% | Selected brand/model must occur in source evidence. |
| Fuel | 10% | Selected fuel type must match. |
| Age | 10% | Year must meet the maximum-age limit. |
| Kilometres | 10% | Mileage must be at or below the selected limit. |

When a criterion is not selected, it receives its neutral full weight. Ranking is deterministic; AI may help coordinate research and word explanations, but cannot change score calculation or ordering.

## AI and search vocabulary

| Term | Meaning |
| --- | --- |
| Orchestrator | The LangGraph workflow and its shared LangChain model that controls the bounded search sequence. |
| Research agent | Agent 1, which selects approved-source searches and calls the Serper middleware. |
| Ranking agent | Agent 2, which applies deterministic scoring and returns the top 10. |
| Candidate | A normalized, deduplicated external result before ranking. |
| Ranked listing | A candidate with rank, match percentage, and explanatory reasons. |
| Snapshot | Stored source evidence at the time of search or save. It is not a live inventory guarantee. |
| Removed | A saved listing whose source returned HTTP 404 or 410 during owner-triggered refresh. |

## Technical boundaries

- `apps/web` presents search, results, and saved-listing experiences.
- `apps/api` owns FastAPI routes, Supabase JWT validation, LangGraph, LangChain agents, provider calls, and repositories.
- `AI_ORCHESTRATION_MODEL_NAME`, currently `gpt-5.4-mini`, is the single model configuration used by the coordinator and both product-search agents.
- The research tool wraps `GoogleSerperRun` and `GoogleSerperAPIWrapper`; it is server-side only.
- LangSmith receives live LangChain/LangGraph traces when enabled. Structured application logs use request IDs and must exclude secrets/tokens.
- Supabase Postgres stores searches, ranked external results, saved external listings, and availability state. Row Level Security protects private customer records.

## Persistence and availability rules

- A durable search stores criteria and its ranked external listings, including raw provider payload, source URL, score, rank, reasons, and retrieval timestamp.
- Saving an external listing references the persisted result; it does not discard the source URL or snapshot.
- Opening `GET /api/v1/saved-listings/{id}` is the only automatic availability check.
- HTTP 404/410 changes the saved record to `removed`; other response codes and temporary network failures do not falsely remove it.
- There are no scheduled checks or automatic deletion jobs.

## Configuration

The API server requires server-only OpenAI, Google Serper, LangSmith, Supabase, and database settings. The key product-search settings are:

```dotenv
AI_ORCHESTRATION_MODEL_NAME=gpt-5.4-mini
PRODUCT_SEARCH_MODE=live
PRODUCT_SEARCH_ALLOWED_CITY=Hyderabad
PRODUCT_SEARCH_MAX_CANDIDATES=100
PRODUCT_SEARCH_TOP_RESULTS=10
```

`PRODUCT_SEARCH_MODE=mock` is required for deterministic unit tests and avoids paid provider calls. Live persistence additionally requires `DATABASE_URL` and the ranked external-listings Supabase migration.

## Operational rules

1. Do not put Serper, OpenAI, LangSmith, database, or Supabase secret credentials in browser configuration.
2. Do not use live Serper or model calls in unit tests.
3. Apply and review migrations before live persistence is enabled.
4. Investigate provider errors and zero-result rates with LangSmith traces and request-correlated application logs.
5. Treat source removal only as a source-status fact; keep the customer’s saved snapshot available for reference.

See [Prompt-PRD-v0Vercel.md](Prompt-PRD-v0Vercel.md) for acceptance requirements and [architecture.md](architecture.md) for system flow.
