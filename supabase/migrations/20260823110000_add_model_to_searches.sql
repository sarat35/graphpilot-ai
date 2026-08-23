alter table public.searches
  add column if not exists model text;

comment on column public.searches.model is 'Optional customer-selected vehicle model for a product search.';
