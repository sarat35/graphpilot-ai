-- BuySeconds Warehouse foundation
--
-- Apply with the Supabase CLI (`supabase db push`) or the Supabase SQL Editor.
-- This migration assumes a Supabase-managed Postgres instance where auth.users,
-- auth.uid(), and pgcrypto are available.

create extension if not exists pgcrypto;

create type public.search_status as enum (
  'queued',
  'ranking',
  'ready',
  'empty',
  'failed'
);

create type public.conversation_status as enum (
  'active',
  'ready_to_search',
  'completed',
  'failed',
  'archived'
);

create type public.message_role as enum ('assistant', 'user', 'system');

create type public.ingestion_status as enum (
  'queued',
  'running',
  'succeeded',
  'failed',
  'partially_succeeded'
);

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text not null check (char_length(trim(display_name)) between 1 and 120),
  default_city text check (char_length(trim(default_city)) between 1 and 120),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.vehicles (
  id uuid primary key default gen_random_uuid(),
  source_name text not null check (char_length(trim(source_name)) between 1 and 120),
  source_listing_id text not null check (char_length(trim(source_listing_id)) between 1 and 255),
  source_url text not null check (source_url ~* '^https://'),
  make text not null check (char_length(trim(make)) between 1 and 120),
  model text not null check (char_length(trim(model)) between 1 and 120),
  variant text,
  year smallint not null check (year between 1950 and 2100),
  fuel_type text not null check (fuel_type in ('Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid')),
  transmission text not null check (transmission in ('Manual', 'Automatic')),
  price_inr integer not null check (price_inr >= 0),
  kilometres integer not null check (kilometres >= 0),
  city text not null check (char_length(trim(city)) between 1 and 120),
  seller_type text not null check (seller_type in ('Dealer', 'Certified Dealer', 'Individual')),
  availability text not null default 'available' check (availability in ('available', 'expired', 'removed')),
  posted_at timestamptz,
  description text,
  condition_notes text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  unique (source_name, source_listing_id)
);

create table public.vehicle_features (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles (id) on delete cascade,
  name text not null check (char_length(trim(name)) between 1 and 160),
  created_at timestamptz not null default timezone('utc', now()),
  unique (vehicle_id, name)
);

create table public.vehicle_media (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles (id) on delete cascade,
  storage_path text not null check (char_length(trim(storage_path)) between 1 and 1024),
  alt_text text,
  sort_order smallint not null default 0 check (sort_order >= 0),
  created_at timestamptz not null default timezone('utc', now()),
  unique (vehicle_id, sort_order)
);

create table public.vehicle_source_snapshots (
  id uuid primary key default gen_random_uuid(),
  vehicle_id uuid not null references public.vehicles (id) on delete cascade,
  provider text not null check (char_length(trim(provider)) between 1 and 120),
  provider_listing_id text not null check (char_length(trim(provider_listing_id)) between 1 and 255),
  payload_json jsonb not null,
  fetched_at timestamptz not null default timezone('utc', now()),
  expires_at timestamptz,
  unique (provider, provider_listing_id, fetched_at)
);

create table public.searches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  city text not null check (char_length(trim(city)) between 1 and 120),
  min_price_inr integer check (min_price_inr is null or min_price_inr >= 0),
  max_price_inr integer check (max_price_inr is null or max_price_inr >= 0),
  brand text,
  fuel_type text check (fuel_type is null or fuel_type in ('Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid')),
  max_age_years smallint check (max_age_years is null or max_age_years between 0 and 100),
  max_kilometres integer check (max_kilometres is null or max_kilometres >= 0),
  status public.search_status not null default 'queued',
  error_code text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  check (max_price_inr is null or min_price_inr is null or max_price_inr >= min_price_inr)
);

create table public.search_results (
  id uuid primary key default gen_random_uuid(),
  search_id uuid not null references public.searches (id) on delete cascade,
  vehicle_id uuid not null references public.vehicles (id) on delete restrict,
  rank smallint not null check (rank between 1 and 5),
  match_score numeric(5, 2) not null check (match_score between 0 and 100),
  match_reasons jsonb not null default '[]'::jsonb check (jsonb_typeof(match_reasons) = 'array'),
  unmatched_reasons jsonb not null default '[]'::jsonb check (jsonb_typeof(unmatched_reasons) = 'array'),
  created_at timestamptz not null default timezone('utc', now()),
  unique (search_id, rank),
  unique (search_id, vehicle_id)
);

create table public.saved_vehicles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  vehicle_id uuid not null references public.vehicles (id) on delete restrict,
  saved_at timestamptz not null default timezone('utc', now()),
  unique (user_id, vehicle_id)
);

create table public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  status public.conversation_status not null default 'active',
  criteria_json jsonb not null default '{}'::jsonb check (jsonb_typeof(criteria_json) = 'object'),
  last_message_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.conversation_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations (id) on delete cascade,
  role public.message_role not null,
  content text not null check (char_length(content) between 1 and 8000),
  tool_data_json jsonb,
  created_at timestamptz not null default timezone('utc', now())
);

create table public.provider_connections (
  id uuid primary key default gen_random_uuid(),
  provider text not null unique check (char_length(trim(provider)) between 1 and 120),
  status text not null default 'inactive' check (status in ('inactive', 'active', 'degraded', 'disabled')),
  config_reference text,
  last_sync_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.ingestion_runs (
  id uuid primary key default gen_random_uuid(),
  provider_connection_id uuid not null references public.provider_connections (id) on delete restrict,
  status public.ingestion_status not null default 'queued',
  started_at timestamptz,
  completed_at timestamptz,
  records_received integer not null default 0 check (records_received >= 0),
  records_written integer not null default 0 check (records_written >= 0),
  error_summary text,
  created_at timestamptz not null default timezone('utc', now())
);

create table public.audit_events (
  id uuid primary key default gen_random_uuid(),
  actor_user_id uuid references public.profiles (id) on delete set null,
  event_type text not null check (char_length(trim(event_type)) between 1 and 120),
  entity_type text not null check (char_length(trim(entity_type)) between 1 and 120),
  entity_id uuid,
  metadata_json jsonb not null default '{}'::jsonb check (jsonb_typeof(metadata_json) = 'object'),
  created_at timestamptz not null default timezone('utc', now())
);

create index vehicles_available_city_idx on public.vehicles (city) where availability = 'available';
create index vehicles_make_model_idx on public.vehicles (make, model);
create index vehicles_search_filter_idx on public.vehicles (fuel_type, price_inr, year, kilometres) where availability = 'available';
create index searches_user_recent_idx on public.searches (user_id, created_at desc);
create index search_results_search_rank_idx on public.search_results (search_id, rank);
create index saved_vehicles_user_recent_idx on public.saved_vehicles (user_id, saved_at desc);
create index conversations_user_recent_idx on public.conversations (user_id, last_message_at desc);
create index conversation_messages_conversation_idx on public.conversation_messages (conversation_id, created_at);
create index ingestion_runs_provider_recent_idx on public.ingestion_runs (provider_connection_id, created_at desc);
create index audit_events_entity_idx on public.audit_events (entity_type, entity_id, created_at desc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

create trigger profiles_set_updated_at before update on public.profiles
for each row execute function public.set_updated_at();
create trigger vehicles_set_updated_at before update on public.vehicles
for each row execute function public.set_updated_at();
create trigger searches_set_updated_at before update on public.searches
for each row execute function public.set_updated_at();
create trigger conversations_set_updated_at before update on public.conversations
for each row execute function public.set_updated_at();
create trigger provider_connections_set_updated_at before update on public.provider_connections
for each row execute function public.set_updated_at();

create or replace function public.create_profile_for_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(nullif(trim(new.raw_user_meta_data ->> 'display_name'), ''), split_part(new.email, '@', 1))
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.create_profile_for_new_user();

create or replace function public.enforce_saved_vehicle_limit()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  if (select count(*) from public.saved_vehicles where user_id = new.user_id) >= 5 then
    raise exception using
      errcode = 'P0001',
      message = 'SAVED_VEHICLE_LIMIT_REACHED',
      detail = 'A member may save at most five vehicles.';
  end if;
  return new;
end;
$$;

create trigger saved_vehicles_limit
  before insert on public.saved_vehicles
  for each row execute function public.enforce_saved_vehicle_limit();

alter table public.profiles enable row level security;
alter table public.vehicles enable row level security;
alter table public.vehicle_features enable row level security;
alter table public.vehicle_media enable row level security;
alter table public.vehicle_source_snapshots enable row level security;
alter table public.searches enable row level security;
alter table public.search_results enable row level security;
alter table public.saved_vehicles enable row level security;
alter table public.conversations enable row level security;
alter table public.conversation_messages enable row level security;
alter table public.provider_connections enable row level security;
alter table public.ingestion_runs enable row level security;
alter table public.audit_events enable row level security;

create policy "members read own profile" on public.profiles
  for select to authenticated using ((select auth.uid()) = id);
create policy "members update own profile" on public.profiles
  for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);

create policy "members read available vehicles" on public.vehicles
  for select to authenticated using (availability = 'available');
create policy "members read vehicle features" on public.vehicle_features
  for select to authenticated using (exists (
    select 1 from public.vehicles v where v.id = vehicle_id and v.availability = 'available'
  ));
create policy "members read vehicle media" on public.vehicle_media
  for select to authenticated using (exists (
    select 1 from public.vehicles v where v.id = vehicle_id and v.availability = 'available'
  ));

create policy "members read own searches" on public.searches
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "members create own searches" on public.searches
  for insert to authenticated with check ((select auth.uid()) = user_id and status = 'queued');
create policy "members update own searches" on public.searches
  for update to authenticated using ((select auth.uid()) = user_id and status = 'queued')
  with check ((select auth.uid()) = user_id and status = 'queued');
create policy "members delete own searches" on public.searches
  for delete to authenticated using ((select auth.uid()) = user_id);

create policy "members read own search results" on public.search_results
  for select to authenticated using (exists (
    select 1 from public.searches s where s.id = search_id and s.user_id = (select auth.uid())
  ));

create policy "members read own saved vehicles" on public.saved_vehicles
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "members save own vehicles" on public.saved_vehicles
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "members remove own saved vehicles" on public.saved_vehicles
  for delete to authenticated using ((select auth.uid()) = user_id);

create policy "members read own conversations" on public.conversations
  for select to authenticated using ((select auth.uid()) = user_id);
create policy "members create own conversations" on public.conversations
  for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "members update own conversations" on public.conversations
  for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "members delete own conversations" on public.conversations
  for delete to authenticated using ((select auth.uid()) = user_id);
create policy "members read own conversation messages" on public.conversation_messages
  for select to authenticated using (exists (
    select 1 from public.conversations c where c.id = conversation_id and c.user_id = (select auth.uid())
  ));
create policy "members create own conversation messages" on public.conversation_messages
  for insert to authenticated with check (role = 'user' and exists (
    select 1 from public.conversations c where c.id = conversation_id and c.user_id = (select auth.uid())
  ));

-- Provider, snapshot, ingestion, and audit shelves intentionally have no
-- authenticated-user policies. They are service-role or operations-only.
