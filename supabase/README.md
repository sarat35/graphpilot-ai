# BuySeconds Supabase database

This directory owns the Postgres Warehouse schema and Row Level Security guards.

## Prerequisites

1. Create a Supabase project with email/password authentication enabled.
2. Install and authenticate the [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started).
3. Link this repository to the project:

   ```sh
   supabase link --project-ref <project-ref>
   ```

## Apply the schema

Review the migration, then apply it to the linked project:

```sh
supabase db push
```

The migration creates the Warehouse shelves, indexes, Supabase Auth profile trigger, five-saved-vehicle guard, and Row Level Security policies.

## Required configuration

Copy `.env.example` to `.env` and set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and the server-only values required by FastAPI. Never expose `SUPABASE_SERVICE_ROLE_KEY` to the Next.js Counter.

## Verification

Use Supabase Studio’s Table Editor to confirm that the expected public tables exist, and use the SQL Editor to inspect the enabled RLS policies. Authentication and repository code are intentionally implemented in the next block.
