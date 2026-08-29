-- Persist normalized external listings and their top-ten ranking for product searches.

alter table public.external_search_results
  drop constraint if exists external_search_results_rank_check;

alter table public.external_search_results
  add constraint external_search_results_rank_check check (rank between 1 and 10),
  add column if not exists source_listing_id text,
  add column if not exists city text,
  add column if not exists make text,
  add column if not exists model text,
  add column if not exists variant text,
  add column if not exists year smallint,
  add column if not exists fuel_type text,
  add column if not exists transmission text,
  add column if not exists seller_type text,
  add column if not exists price_inr integer check (price_inr is null or price_inr >= 0),
  add column if not exists kilometres integer check (kilometres is null or kilometres >= 0),
  add column if not exists image_url text,
  add column if not exists availability text not null default 'available'
    check (availability in ('available', 'expired', 'removed')),
  add column if not exists match_percentage smallint check (match_percentage between 0 and 100),
  add column if not exists match_reasons jsonb not null default '[]'::jsonb,
  add column if not exists unmatched_or_missing_reasons jsonb not null default '[]'::jsonb,
  add column if not exists retrieved_at timestamptz;

create table if not exists public.saved_external_listings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  external_search_result_id uuid not null references public.external_search_results (id) on delete restrict,
  availability text not null default 'available'
    check (availability in ('available', 'expired', 'removed')),
  last_checked_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  unique (user_id, external_search_result_id)
);

create index if not exists saved_external_listings_user_recent_idx
  on public.saved_external_listings (user_id, created_at desc);

alter table public.saved_external_listings enable row level security;

create policy "members read own saved external listings" on public.saved_external_listings
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "members save own external listings" on public.saved_external_listings
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "members update own saved external listings" on public.saved_external_listings
  for update to authenticated using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
create policy "members remove own saved external listings" on public.saved_external_listings
  for delete to authenticated using ((select auth.uid()) = user_id);
