# BuySeconds — Product Requirements Document

## 1. Product summary

BuySeconds is an authenticated used-car discovery experience. In this release it searches **Hyderabad only**, discovers public listings from approved marketplaces, and returns an explainable top-10 shortlist. Every result retains its original source link and never presents unavailable source data as fact.

## 2. Goals and non-goals

### Goals

- Let a signed-in customer search Hyderabad listings by budget, brand, model, fuel type, maximum age, and maximum kilometres.
- Research up to 100 unique candidates across Cars24, CarWale, CarTrade, Spinny, and OLX; rank and return the best 10.
- Use LangGraph for workflow orchestration and LangChain agents/tools for research and ranking.
- Persist searches, ranked external listings, and source links in Supabase/Postgres.
- Let a customer save an external listing and retain its snapshot if the original listing is later removed.
- Trace graph, model, and tool activity with LangSmith and correlation-aware server logs.

### Non-goals

- Search cities other than Hyderabad in this release.
- Invent, guarantee, or independently verify price, year, mileage, availability, or condition.
- Run scheduled listing-refresh jobs. A saved listing refreshes only when its owner opens it.
- Expose server credentials, raw authorization tokens, or unredacted provider secrets.
- Add payments, dealer administration, or marketplace inventory management.

## 3. Technology requirements

| Layer | Required technology |
| --- | --- |
| Customer interface | Next.js App Router, React, TypeScript, Tailwind CSS |
| Authentication | Supabase Auth email/password and JWT validation |
| API | Async Python FastAPI under `/api/v1` |
| Validation | Pydantic |
| AI orchestration | LangGraph using `AI_ORCHESTRATION_MODEL_NAME` |
| AI agents/tools | LangChain, `ChatOpenAI`, `GoogleSerperRun`, `GoogleSerperAPIWrapper` |
| Observability | LangSmith plus structured server logs |
| Persistence | Supabase Postgres migrations and Row Level Security |

## 4. Search workflow requirements

1. The API accepts only `city=Hyderabad`; other cities return a validation error.
2. The LangGraph workflow performs: validate → orchestrate → research → normalize/deduplicate → rank → persist → respond.
3. The shared model is configured once through `AI_ORCHESTRATION_MODEL_NAME`, initially `gpt-5.4-mini`, and is used by the LangGraph coordinator, research agent, and ranking agent in live mode.
4. Agent 1 uses LangChain middleware around Google Serper to issue marketplace-scoped Hyderabad queries. It must retain raw source evidence, permit only the approved domains, and return no more than 100 unique candidates.
5. Agent 2 ranks candidates deterministically. The model may assist with workflow/rationale wording but cannot alter calculated scores or ranks.
6. Missing source fields remain `null` and are explicitly described as missing; the service must not infer them.
7. The response returns no more than 10 ranked listings, including source URL, marketplace, normalized fields, availability, rank, integer match percentage, matching reasons, and missing/non-matching reasons.

### Ranking weights

| Criterion | Weight |
| --- | ---: |
| Hyderabad city evidence | 20% |
| Price range | 25% |
| Brand and model | 25% |
| Fuel type | 10% |
| Maximum age | 10% |
| Maximum kilometres | 10% |

If a criterion is not selected, it receives its full neutral weight. A missing source value receives no credit and produces an explanatory reason. A confirmed non-Hyderabad listing is excluded.

## 5. Data and saved-listing requirements

- Store external listing snapshots, raw source payload, retrieved timestamp, rank, score, reasons, and source URL with the customer search.
- A saved external listing references the persisted search result and retains its snapshot and source URL.
- `GET /api/v1/saved-listings/{id}` refreshes the source URL for its owner. A 404 or 410 marks the saved listing `removed`; temporary network/provider errors do not remove it.
- No scheduled refresh is performed.
- Existing Row Level Security policies must ensure customers access only their own searches and saved external listings.

## 6. Configuration and observability

Required server settings include:

```dotenv
AI_ORCHESTRATION_MODEL_NAME=gpt-5.4-mini
PRODUCT_SEARCH_MODE=live
PRODUCT_SEARCH_ALLOWED_CITY=Hyderabad
PRODUCT_SEARCH_ALLOWED_DOMAINS=cars24.com,carwale.com,cartrade.com,spinny.com,olx.in
PRODUCT_SEARCH_MAX_CANDIDATES=100
PRODUCT_SEARCH_TOP_RESULTS=10
GOOGLE_SERPER_API_KEY=...
LANGSMITH_TRACING_V2=true
```

LangSmith traces all live LangChain/LangGraph model and tool activity. Application logs include request IDs, candidate counts, ranking completion, persistence, and recoverable failures, while excluding credentials and tokens.

## 7. Acceptance criteria

- A Hyderabad search can collect up to 100 approved-source candidates and return at most 10 deduplicated rankings.
- A Bengaluru or Pune request is rejected before external research begins.
- A result score exactly follows the configured 20/25/25/10/10/10 weighting and includes reasons.
- Every returned listing includes a source link; unknown evidence is represented as missing, not guessed.
- A customer can save a persisted external result; opening that saved record refreshes availability and preserves a removed snapshot.
- Live model and Serper calls use the single orchestration-model setting and are visible in LangSmith when tracing is enabled.
- Backend tests run in mock mode; no unit test requires paid provider calls.

## 8. Delivery and operations

Apply the Supabase migration before enabling durable live searches. Configure `DATABASE_URL`, Supabase authentication settings, OpenAI, Serper, and LangSmith credentials only on the API server. Run the backend test, lint, and formatting checks before release.

See [architecture.md](architecture.md) and [knowledge-base.md](knowledge-base.md) for the system design and operating rules.
