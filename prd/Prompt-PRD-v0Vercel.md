Build the BuySeconds MVP described in the attached PRD.

## Implementation contract

Create a front-end-only prototype using:

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide icons
- Responsive, mobile-first layouts
- Reusable components
- Accessible semantic HTML

## Critical scope restrictions

- Do not connect Supabase.
- Do not implement real authentication.
- Do not create a database.
- Do not create API routes or Server Actions.
- Do not perform web scraping or live internet searches.
- Do not call external marketplace APIs.
- Do not request API keys or environment variables.
- Do not add payment functionality.
- Do not invent administrator pages.

Use deterministic local mock data and simulated asynchronous services for:

- Sign-in and sign-up
- Protected-route behaviour
- Car searching and ranking
- Saving and removing cars
- Five recent searches
- Five-car saved limit
- Chatbot conversations
- Loading, empty, success, offline and failure states

Store mock session and prototype state in browser storage where persistence
is useful. Clearly label all listings as demonstration data.

## Required routes

- `/`
- `/auth/signin`
- `/auth/signup`
- `/search`
- `/results`
- `/product/[id]`
- `/products`
- `/chatbot`
- `/account`

Use a shared authenticated layout for:

- Desktop sidebar navigation
- Mobile bottom navigation
- Floating chatbot launcher

Use URL search parameters on `/results` so search criteria survive refresh
and can be shared. Use `router.replace()` when refining criteria.

## Product decisions

- Search uses a guided step-by-step form.
- Results display exactly five cars.
- Results use a ranked comparison-list layout.
- Selecting a car opens its internal detail page first.
- The external marketplace link opens in a new tab.
- Customers can save a maximum of five cars.
- Saving a sixth car opens a replacement dialog.
- Display the five most recent searches separately.
- Provide both a floating chatbot and a full `/chatbot` page.
- Use a deterministic catalogue of ten mock cars.

## Build process

Do not attempt to design every page immediately.

For the first iteration:

1. Review the PRD.
2. Summarize the routes, shared layouts and reusable components.
3. Identify any contradictions without changing the requirements.
4. Create the application shell and navigation.
5. Create the local mock-data models.
6. Build only:
   - Landing page
   - Sign-in page
   - Sign-up page
   - Search-page shell
7. Ensure the application compiles without TypeScript errors.

After completing the first iteration, stop and summarize:

- Pages created
- Components created
- Mock services created
- Assumptions made
- Features remaining

Do not add functionality that is not specified in the PRD.
