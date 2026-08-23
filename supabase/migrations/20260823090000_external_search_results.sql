create table public.external_search_results (
  id uuid primary key default gen_random_uuid(),
  search_id uuid not null references public.searches (id) on delete cascade,
  rank smallint not null check (rank between 1 and 5),
  title text not null check (char_length(title) between 1 and 300),
  source_url text not null check (source_url ~* '^https://'),
  source_name text not null check (char_length(source_name) between 1 and 120),
  snippet text not null default '',
  raw_result_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  unique (search_id, rank)
);

create index external_search_results_search_rank_idx on public.external_search_results (search_id, rank);

alter table public.external_search_results enable row level security;

create policy "members read own external search results" on public.external_search_results
  for select to authenticated using (exists (
    select 1 from public.searches s where s.id = search_id and s.user_id = (select auth.uid())
  ));
