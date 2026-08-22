# BuySeconds MVP — Front-End Product Requirements Document

**Document status:** Ready for v0 prototyping
**Scope:** Next.js front-end UI and simulated interactions only
**Primary product:** Second-hand cars
**Delivery context:** Generated and iterated in v0 by Vercel using the Next.js App Router

## 1. Project Overview

BuySeconds is a responsive product-discovery experience for customers looking for second-hand goods, beginning with used cars. Rather than manually reviewing many marketplace listings, a customer provides location and vehicle criteria through a guided search or conversational assistant. The interface presents the five best matching mock listings in a ranked comparison list, explains why each result matches, and links to its illustrative marketplace source.

The MVP serves public visitors evaluating the service and signed-in customers searching, reviewing, and saving cars. It validates the user journey and presentation model before live marketplace search, Supabase authentication, database persistence, or Row Level Security are implemented. All data-dependent behaviour must therefore use mock data and believable simulated loading, success, empty, error, authentication, and rollback states.

Primary customer goals are to describe a desired car quickly, compare credible choices, inspect a promising vehicle, continue to the source listing, and retain a shortlist. Business objectives are to validate search completion, result engagement, save intent, and chatbot adoption. Prototype success indicators include landing-to-sign-up clicks, completed searches, result-detail opens, external-source clicks, cars saved, and guided-chat completion.

## 2. User Types and Permissions

### Public visitor

A visitor may view only the landing page, sign-in page, and sign-up page. The landing page explains the product and provides repeated sign-up calls to action. Attempting to open a protected URL shows a brief redirect state and sends the visitor to `/auth/signin`. A visitor cannot search, view results, save cars, access recent searches, use the authenticated chatbot, or open account settings.

### Signed-in customer

A customer may access Search, Results, Product Detail, My Products, Chatbot, and Account. The customer can complete guided searches, view five ranked results, inspect internal product details, open the external source, save or remove cars, revisit the five most recent searches, and sign out. A customer may save at most five cars. Saving a sixth opens a replacement dialog so removal is explicit; the UI never silently discards a saved car.

There are no administrators, subscription tiers, or organisation roles in this MVP. Authentication, authorization, persistence, and RLS are future implementation dependencies. The prototype simulates signed-in and signed-out states with front-end fixtures. An authenticated customer opening `/`, `/auth/signin`, or `/auth/signup` is redirected to `/search`. Shared protected links preserve their intended destination so a visitor can return after simulated sign-in.

## 3. Navigation and Information Architecture

Public pages use a compact top navigation with BuySeconds branding, Sign In, and Sign Up. Signed-in desktop pages use a persistent left sidebar containing Search, My Products, Chatbot, and Account. The current destination is clearly identified. A compact account summary and Sign Out action sit at the bottom. Signed-in mobile pages replace the sidebar with a fixed four-item bottom navigation using the same destinations. The chatbot launcher floats above the bottom navigation and remains available on Search, Results, Product Detail, and My Products; it is hidden on the full Chatbot page.

### Route hierarchy

- `/` — public marketing landing page
- `/auth/signin` — public sign-in page
- `/auth/signup` — public account-creation page
- `/search` — protected guided car-search page
- `/results` — protected ranked comparison list; criteria stored in URL parameters
- `/product/:id` — protected internal listing detail; implemented in Next.js as `app/product/[id]/page.tsx`
- `/products` — protected Saved Cars and Recent Searches
- `/chatbot` — protected expanded conversational search
- `/account` — protected account and preference settings

No breadcrumbs are needed on landing, authentication, Search, My Products, Chatbot, or Account. Product Detail uses `Results / Car name`, with Results returning to the same URL criteria. Results displays a compact search summary and an Edit Search action. URL parameters restore search state on reload and support shareable links. Changing a result filter updates the URL without creating excessive browser-history entries. An external marketplace link opens in a new tab and is explicitly labelled “View original listing.”

## 4. Core User Flows

### Flow 1: Visitor conversion and simulated authentication

**Entry point:** `/`
**Prerequisites:** None.

1. Visitor reviews the value proposition and How It Works explanation.
2. Visitor selects Get Started or Sign Up → `/auth/signup` opens.
3. Visitor enters name, email, password, and password confirmation → fields validate on blur.
4. Valid submission shows progress, simulates account creation, and redirects to `/search`.
5. A returning visitor may select Sign In, submit valid mock credentials, and continue to Search or the originally requested protected URL.

**Success:** Authenticated shell and guided-search introduction appear.
**Errors:** Invalid email, short password, mismatch, invalid credentials, or simulated network failure displays an inline recovery message.
**Alternative:** Sign-in and sign-up pages cross-link.

### Flow 2: Guided car discovery

**Entry point:** `/search`
**Prerequisites:** Simulated signed-in customer.

1. Customer sees five recent searches and selects Start New Search or Reuse Search.
2. A step-by-step form asks city, price range, brand, fuel type, maximum vehicle age, and maximum kilometres.
3. Each step validates input; Back preserves answers and Skip is available only for optional criteria.
4. Review displays all criteria with Edit links. At least one preference plus city is required.
5. Find Cars triggers a simulated search state and navigates to `/results` with URL parameters.

**Success:** Five mock cars appear ranked by match percentage.
**Errors:** No match offers Edit Criteria and Clear Optional Filters; failure offers Retry.
**Alternative:** A recent search may be rerun or its criteria edited.

### Flow 3: Compare, inspect, and visit source

**Entry point:** `/results`
**Prerequisites:** Valid search criteria.

1. Customer scans an aligned comparison list containing rank, image, vehicle, price, age, fuel, kilometres, city, source, and match.
2. Customer refines a criterion → skeleton rows appear and the URL/result set updates.
3. Customer selects a result → `/product/:id` opens.
4. Detail page explains matched and unmatched criteria and displays listing information.
5. Customer selects View Original Listing → illustrative marketplace destination opens in a new tab.

**Success:** Customer identifies a suitable car or proceeds to its source.
**Errors:** Missing/expired mock listing offers Back to Results and Find Similar Cars.
**Alternative:** Save directly from Results or Detail.

### Flow 4: Manage saved cars and recent searches

**Entry point:** Save action or `/products`
**Prerequisites:** Signed in.

1. Customer saves a result → optimistic saved state and confirmation toast appear.
2. My Products shows Saved Cars first and the five most recent searches below, newest first.
3. Customer removes a saved car → confirmation appears only when removal is consequential; the mock service may demonstrate rollback failure.
4. When five cars are already saved, Save opens a replacement dialog listing the five cars.
5. Selecting one replacement removes it and saves the new car; Cancel makes no change.

**Success:** Saved list accurately reflects the intended five cars.
**Errors:** Simulated save/delete failure restores the previous state and offers Retry.
**Alternative:** A saved car opens Product Detail; a recent search opens Results.

### Flow 5: Conversational discovery

**Entry point:** Floating launcher or `/chatbot`
**Prerequisites:** Signed in.

1. Assistant asks what product the customer wants; MVP recognizes used-car intent.
2. It asks one question at a time using choices plus free text: city, budget, brand, fuel, age, and kilometres.
3. Customer may edit or remove collected criteria shown as a live summary.
4. Assistant asks for confirmation and enables Find Cars.
5. Submission closes the floating panel or leaves the full page and opens `/results` with equivalent criteria.

**Success:** Chat-generated search produces the same ranked-list experience.
**Errors:** Unsupported product explains the cars-only MVP; unclear answers ask for clarification; simulated failure preserves the conversation and offers Retry.
**Alternative:** Expand the floating conversation into `/chatbot` without losing progress.

## 5. Detailed Page Specifications

### Landing Page

**Route:** `/` · **Access:** Public visitors · **Purpose:** Explain the value and convert visitors.

**Layout map:** Top navigation → hero and Get Started → three-step How It Works → four benefit callouts → final CTA → simple footer. The hero communicates “Tell us what used car you need; compare the five best matches.” Actions route to Sign Up or Sign In. Loading is unnecessary beyond image placeholders. If authenticated, show a short redirect to Search. On mobile, navigation condenses while keeping one prominent CTA. Footer links may be non-functional prototype placeholders but must be visibly identified.

### Sign Up Page

**Route:** `/auth/signup` · **Access:** Public visitors · **Purpose:** Simulate account creation.

**Layout map:** Brand/back link → concise benefit statement → name, email, password, confirmation → Create Account → Sign In link. Validate on blur; disable submission until valid. Password rules remain visible. Loading changes the action label without shifting layout. Errors appear inline and in a form-level alert when appropriate. Success redirects to Search. Mobile uses a single full-width form. Prevent duplicate submission and preserve non-sensitive fields after simulated failure.

### Sign In Page

**Route:** `/auth/signin` · **Access:** Public visitors · **Purpose:** Restore a customer session.

**Layout map:** Brand/back link → email and password → Sign In → Forgot Password placeholder → Sign Up link. Invalid credentials show “Invalid email or password” without identifying which field failed. Network failure shows “Check your internet connection.” The intended protected route is preserved. Authenticated customers are redirected to `/search`. Mobile keeps the action visible above the keyboard where practical.

### Search Page

**Route:** `/search` · **Access:** Signed-in customers · **Purpose:** Collect search criteria through a guided journey.

**Layout map:** Authenticated navigation → page title and short instruction → recent-search strip → step card → progress indicator → Back/Continue. Steps are City, Budget, Brand, Fuel, Age, Kilometres, and Review. Show selectable suggestions and free entry where appropriate. Fields validate on blur; autocomplete waits briefly before suggestions. Review displays editable criteria. Loading uses a progress narrative such as “Comparing available listings.” Empty recent history offers Start Your First Search. A restored draft is labelled and can be cleared. Mobile shows one step per screen above the bottom navigation.

### Results Page

**Route:** `/results?[criteria]` · **Access:** Signed-in customers · **Purpose:** Compare the five strongest matches.

**Layout map:** Navigation → search-summary bar → refine controls → ranked comparison header → five aligned result rows → feedback/retry region. Primary data are image, rank, make/model/variant, year, price, fuel, kilometres, city, seller/source, match percentage, and save status. Selecting a row opens Product Detail; Save does not trigger row navigation. Sorting defaults to Best Match, with Price Low–High and Newest alternatives. Skeleton rows preserve columns while loading. Mobile converts rows into stacked cards with the same field order. If no result matches, show the exact criteria, Edit Search, and Clear Optional Filters.

### Product Detail Page

**Route:** `/product/:id` · **Access:** Signed-in customers · **Purpose:** Build confidence before source redirection.

**Layout map:** Breadcrumb → image gallery → title, price, match, and actions → key specifications → match explanation → seller/source summary → disclaimer. Actions are Save/Remove, View Original Listing, Back to Results, and Find Similar Cars. External navigation opens a new tab. Missing listing uses an expired state rather than a generic 404. Image failure falls back to a vehicle placeholder. Mobile uses a sticky bottom action area without obscuring content. The page clearly states that availability and price must be verified with the source.

### My Products Page

**Route:** `/products` · **Access:** Signed-in customers · **Purpose:** Manage a five-car shortlist and rerun recent searches.

**Layout map:** Navigation → Saved Cars heading with `n/5` counter → saved comparison cards/list → Recent Searches heading → five newest criteria summaries. Saved-car actions are View, Remove, and View Source. Recent-search actions are Rerun, Edit, and Remove from History. Empty Saved Cars points to Search; empty history points to Start a Search. Optimistic removal can revert with an error toast. The sixth-save replacement dialog is accessible from here and from result pages. Mobile displays compact vertical cards and horizontally scrollable criteria chips.

### Chatbot Page and Floating Panel

**Route:** `/chatbot` plus global launcher · **Access:** Signed-in customers · **Purpose:** Build a search conversationally.

**Layout map:** On full page, navigation → conversation history → live criteria summary → composer and suggested replies. The floating panel contains the same journey in reduced space, with Expand and Close controls. Messages ask one question at a time. Criteria chips can be edited or removed. Find Cars becomes active after city and at least one preference are confirmed. Typing, retry, unsupported-product, and offline states are simulated. Closing preserves the draft. Mobile full page uses the available height above bottom navigation; the floating view expands to a near-full-screen sheet.

### Account Page

**Route:** `/account` · **Access:** Signed-in customers · **Purpose:** Display identity, preferences, and sign-out controls.

**Layout map:** Navigation → profile summary → default search city and optional preferences → session actions → Sign Out. Editing is simulated with Save/Cancel and success/error feedback. Sign Out clears mock session state and returns to Landing. Destructive account deletion is excluded. Mobile uses stacked sections and keeps Sign Out separated from ordinary preferences.

## 6. Mock Data Strategy

Create `mock-products` with 10 realistic used-car records distributed across multiple Indian cities, brands, fuel types, price bands, ages, and kilometre ranges. Each record includes ID, make, model, variant, year, fuel type, transmission, price, kilometres, city, image, marketplace name, illustrative source URL, seller type, posted date, availability, features, description, and condition notes. Match percentage and match reasons are derived by a deterministic mock-ranking function so results feel consistent.

Create mock customers, five saved-car IDs, five recent-search records, conversation messages, and state fixtures for loading, empty, search error, expired listing, offline, and optimistic rollback. Use representative marketplace names, but label all listings as demo data and avoid live claims. Required mock services include search, rank, get product, save, replace saved car, remove, recent-search management, sign-in/sign-up, and chatbot response simulation. Hardcoded TypeScript fixtures are preferred over randomized generation because visual reviews and v0 iterations require repeatable results.

## 7. Interaction Patterns and Micro-interactions

Use full pages for Search, Results, Product Detail, My Products, Chatbot, and Account. Use a floating panel for quick chatbot access, a dialog for replacing one of five saved cars, and a confirmation dialog only for meaningful removals. Save/Remove uses optimistic feedback with rollback. Toasts confirm non-blocking success and recoverable failure; inline messages handle form errors. Match indicators animate once when results load, while skeletons prevent layout shift. Hover reveals row emphasis and external-link intent; keyboard focus provides the equivalent cue. Search progress, chatbot typing, and source-opening indicators should feel responsive without implying real network activity.

## 8. Edge Cases and Error Handling

Every data page supports loading, empty, error, and success states. Search with insufficient criteria disables Find Cars and explains what is missing. No results says: “No cars match your current criteria. Try adjusting or removing an optional filter.” Search failure says: “Couldn’t load cars. Please try again,” with Retry. Offline state says: “Check your internet connection,” while preserving criteria and conversation.

Forms validate on blur with “Enter a valid email,” “Password must be 8+ characters,” and “Passwords don’t match.” Authentication failure does not reveal account existence. Save/delete failures revert optimistic changes and retain the five-car counter. A sixth save always requires explicit replacement. An expired source listing offers similar results. Invalid product IDs show a product-specific not-found state. Unauthorized protected access redirects to Sign In; authenticated access to public auth pages redirects to Search. Long names, missing images, duplicate results, unusually high kilometres, zero optional filters, and direct URL reloads must not break the layout.

## 9. Performance and UX Considerations

The MVP displays exactly five results, so pagination and Show More are excluded. Lazy-load vehicle images, debounce autocomplete by 300 ms, preserve result dimensions with skeletons, and update filters without a full page reload. Keep optimistic saves reversible. URL criteria must restore a shared or refreshed Results page.

## 10. Implementation Checklist

### Landing and Authentication

- [ ] Build Landing, Sign In, and Sign Up layouts with responsive states
- [ ] Add validation, simulated authentication, redirects, and failures

### Search and Results

- [ ] Build seven-step guided search and five recent searches
- [ ] Implement URL-restored criteria and five-row ranked comparison
- [ ] Add loading, empty, retry, offline, and mobile states

### Product and Saved Cars

- [ ] Build Product Detail and external-source transition
- [ ] Build My Products with five-car limit and replacement dialog
- [ ] Add optimistic save/remove with rollback simulation

### Chatbot and Account

- [ ] Build persistent floating chatbot and expanded `/chatbot` flow
- [ ] Build Account preferences and simulated sign-out

### Final Validation

- [ ] Verify all routes, protected redirects, deep links, focus order, and responsive layouts
- [ ] Test new user, returning user, guided search, chatbot search, save-limit, empty, error, and sign-out flows

## Front-End Scope Guardrails for v0

- Generate a Next.js App Router application. Use navigable pages for every specified route and a shared authenticated layout for the sidebar/bottom navigation.
- Keep the UX route notation `/product/:id`; implement the dynamic segment as `/product/[id]` in the Next.js file structure.
- Use URL search parameters for restorable search criteria. Refinements should update the current Results URL without adding unnecessary browser-history entries.
- Use Next.js navigation primitives for internal routes and an ordinary external link, opening in a new tab with safe external-link behaviour, for marketplace destinations.
- Use local deterministic fixtures and front-end state for the prototype. A page refresh may reset simulated authentication and unsaved state unless browser-storage simulation is deliberately added.
- Do not connect Supabase, marketplace APIs, web scraping, server actions, databases, or real authentication.
- Do not claim mock listings are currently available; mark them as demonstration data.
- Build all flows with deterministic fixtures and simulated async states.
- Preserve the route structure and selected UX decisions when iterating.
- Treat live data acquisition, legal marketplace access, authentication, persistence, security, and RLS as a later implementation phase.
