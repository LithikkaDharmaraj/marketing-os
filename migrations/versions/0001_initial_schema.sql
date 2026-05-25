-- Marketing OS — Initial Schema Migration
-- Run via: psql $DATABASE_URL -f migrations/versions/0001_initial_schema.sql

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- ENUMS
-- ============================================================
DO $$ BEGIN
  CREATE TYPE workflow_status AS ENUM (
    'pending','queued','scraping','cleaning','extracting',
    'positioning','icp_generating','embedding','completed','failed','partial'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE scrape_status AS ENUM ('pending','running','completed','failed','skipped');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE tenant_plan AS ENUM ('trial','starter','growth','enterprise');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('owner','admin','member','viewer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ============================================================
-- TENANTS
-- ============================================================
CREATE TABLE IF NOT EXISTS tenants (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  slug          VARCHAR(63) UNIQUE NOT NULL,
  name          VARCHAR(255) NOT NULL,
  plan          tenant_plan NOT NULL DEFAULT 'trial',
  status        VARCHAR(50) NOT NULL DEFAULT 'active',
  settings      JSONB NOT NULL DEFAULT '{}',
  usage_quota   JSONB NOT NULL DEFAULT '{"scrapes_per_month":100,"ai_calls_per_month":500}',
  usage_current JSONB NOT NULL DEFAULT '{"scrapes":0,"ai_calls":0}',
  trial_ends_at TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_tenants_slug   ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status) WHERE deleted_at IS NULL;

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id        UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email            VARCHAR(255) NOT NULL,
  full_name        VARCHAR(255),
  role             user_role NOT NULL DEFAULT 'member',
  auth_provider    VARCHAR(50) NOT NULL DEFAULT 'email',
  password_hash    VARCHAR(255),
  is_verified      BOOLEAN NOT NULL DEFAULT FALSE,
  last_login_at    TIMESTAMPTZ,
  preferences      JSONB NOT NULL DEFAULT '{}',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at       TIMESTAMPTZ,
  UNIQUE(tenant_id, email)
);
CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_email  ON users(email)     WHERE deleted_at IS NULL;

-- ============================================================
-- COMPANIES
-- ============================================================
CREATE TABLE IF NOT EXISTS companies (
  id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id            UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name                 VARCHAR(255) NOT NULL,
  domain               VARCHAR(255),
  website_url          VARCHAR(1024),
  linkedin_url         VARCHAR(1024),
  crunchbase_url       VARCHAR(1024),
  description          TEXT,
  industry             VARCHAR(255),
  sub_industry         VARCHAR(255),
  business_model       VARCHAR(100),
  company_size         VARCHAR(50),
  employee_count       INTEGER,
  founded_year         INTEGER,
  headquarters_city    VARCHAR(255),
  headquarters_country VARCHAR(100),
  geography            VARCHAR(255),
  funding_stage        VARCHAR(100),
  total_funding_usd    BIGINT,
  annual_revenue_range VARCHAR(100),
  pricing_range        VARCHAR(100),
  tech_stack           JSONB NOT NULL DEFAULT '[]',
  social_profiles      JSONB NOT NULL DEFAULT '{}',
  intake_data          JSONB NOT NULL DEFAULT '{}',
  enriched_data        JSONB NOT NULL DEFAULT '{}',
  intelligence_status  workflow_status NOT NULL DEFAULT 'pending',
  workflow_run_id      UUID,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at           TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_companies_tenant   ON companies(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_companies_domain   ON companies(domain)    WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_intake   ON companies USING GIN(intake_data);
CREATE INDEX IF NOT EXISTS idx_companies_enriched ON companies USING GIN(enriched_data);

-- ============================================================
-- CONTACTS
-- ============================================================
CREATE TABLE IF NOT EXISTS contacts (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id    UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id   UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  full_name    VARCHAR(255),
  email        VARCHAR(255),
  phone        VARCHAR(50),
  linkedin_url VARCHAR(1024),
  job_title    VARCHAR(255),
  seniority    VARCHAR(100),
  department   VARCHAR(100),
  is_founder   BOOLEAN DEFAULT FALSE,
  is_primary   BOOLEAN DEFAULT FALSE,
  contact_type VARCHAR(50) DEFAULT 'general',
  raw_data     JSONB NOT NULL DEFAULT '{}',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at   TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_email_company
  ON contacts(company_id, email)
  WHERE deleted_at IS NULL AND email IS NOT NULL;

-- ============================================================
-- PRODUCTS
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name            VARCHAR(255) NOT NULL,
  tagline         VARCHAR(500),
  description     TEXT,
  product_type    VARCHAR(100),
  pricing_model   VARCHAR(100),
  pricing_range   VARCHAR(100),
  pricing_tiers   JSONB NOT NULL DEFAULT '[]',
  core_features   JSONB NOT NULL DEFAULT '[]',
  differentiators JSONB NOT NULL DEFAULT '[]',
  integrations    JSONB NOT NULL DEFAULT '[]',
  target_use_cases JSONB NOT NULL DEFAULT '[]',
  problems_solved JSONB NOT NULL DEFAULT '[]',
  target_market   TEXT,
  goals           JSONB NOT NULL DEFAULT '[]',
  raw_intake      JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at      TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_products_company ON products(company_id) WHERE deleted_at IS NULL;

-- ============================================================
-- SCRAPED PAGES
-- ============================================================
CREATE TABLE IF NOT EXISTS scraped_pages (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  apify_run_id    VARCHAR(255),
  apify_actor_id  VARCHAR(255),
  source_type     VARCHAR(100) NOT NULL,
  source_url      VARCHAR(2048) NOT NULL,
  status          scrape_status NOT NULL DEFAULT 'pending',
  raw_content     TEXT,
  structured_data JSONB NOT NULL DEFAULT '{}',
  metadata        JSONB NOT NULL DEFAULT '{}',
  content_hash    VARCHAR(64),
  scraped_at      TIMESTAMPTZ,
  retry_count     INTEGER NOT NULL DEFAULT 0,
  error_detail    TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_scraped_pages_company ON scraped_pages(company_id);
CREATE INDEX IF NOT EXISTS idx_scraped_pages_source  ON scraped_pages(source_type, status);
CREATE INDEX IF NOT EXISTS idx_scraped_pages_hash    ON scraped_pages(content_hash);
CREATE INDEX IF NOT EXISTS idx_scraped_pages_data    ON scraped_pages USING GIN(structured_data);

-- ============================================================
-- ENRICHMENT DATA
-- ============================================================
CREATE TABLE IF NOT EXISTS enrichment_data (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id        UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id       UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  data_source      VARCHAR(100) NOT NULL,
  data_type        VARCHAR(100) NOT NULL,
  raw_data         JSONB NOT NULL DEFAULT '{}',
  normalized_data  JSONB NOT NULL DEFAULT '{}',
  confidence_score FLOAT,
  is_current       BOOLEAN NOT NULL DEFAULT TRUE,
  fetched_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at       TIMESTAMPTZ,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_enrichment_company ON enrichment_data(company_id, is_current);
CREATE INDEX IF NOT EXISTS idx_enrichment_source  ON enrichment_data(data_source, data_type);

-- ============================================================
-- COMPETITORS
-- ============================================================
CREATE TABLE IF NOT EXISTS competitors (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id         UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id        UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  competitor_name   VARCHAR(255) NOT NULL,
  competitor_domain VARCHAR(255),
  competitor_url    VARCHAR(1024),
  positioning       TEXT,
  pricing_signals   JSONB NOT NULL DEFAULT '{}',
  features          JSONB NOT NULL DEFAULT '[]',
  weaknesses        JSONB NOT NULL DEFAULT '[]',
  messaging         JSONB NOT NULL DEFAULT '{}',
  target_audience   JSONB NOT NULL DEFAULT '[]',
  raw_scraped       JSONB NOT NULL DEFAULT '{}',
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at        TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_competitors_company ON competitors(company_id);

-- ============================================================
-- POSITIONING PROFILES
-- ============================================================
CREATE TABLE IF NOT EXISTS positioning_profiles (
  id                     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id              UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id             UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  version                INTEGER NOT NULL DEFAULT 1,
  is_current             BOOLEAN NOT NULL DEFAULT TRUE,
  is_approved            BOOLEAN NOT NULL DEFAULT FALSE,
  status                 workflow_status NOT NULL DEFAULT 'pending',
  core_positioning       JSONB NOT NULL DEFAULT '{}',
  segment_positioning    JSONB NOT NULL DEFAULT '[]',
  messaging_angles       JSONB NOT NULL DEFAULT '[]',
  emotional_triggers     JSONB NOT NULL DEFAULT '[]',
  competitive_moats      JSONB NOT NULL DEFAULT '[]',
  value_propositions     JSONB NOT NULL DEFAULT '[]',
  objection_handling     JSONB NOT NULL DEFAULT '[]',
  raw_ai_output          JSONB NOT NULL DEFAULT '{}',
  model_used             VARCHAR(100),
  prompt_tokens          INTEGER,
  completion_tokens      INTEGER,
  confidence_score       FLOAT,
  generated_at           TIMESTAMPTZ,
  approved_at            TIMESTAMPTZ,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at             TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_positioning_company ON positioning_profiles(company_id, is_current);

-- ============================================================
-- ICP PROFILES
-- ============================================================
CREATE TABLE IF NOT EXISTS icp_profiles (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id         UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id        UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  profile_name      VARCHAR(255) NOT NULL,
  version           INTEGER NOT NULL DEFAULT 1,
  is_current        BOOLEAN NOT NULL DEFAULT TRUE,
  is_approved       BOOLEAN NOT NULL DEFAULT FALSE,
  firmographics     JSONB NOT NULL DEFAULT '{}',
  psychographics    JSONB NOT NULL DEFAULT '{}',
  job_titles        JSONB NOT NULL DEFAULT '[]',
  seniority_levels  JSONB NOT NULL DEFAULT '[]',
  departments       JSONB NOT NULL DEFAULT '[]',
  buying_triggers   JSONB NOT NULL DEFAULT '[]',
  pain_points       JSONB NOT NULL DEFAULT '[]',
  objections        JSONB NOT NULL DEFAULT '[]',
  decision_makers   JSONB NOT NULL DEFAULT '[]',
  channels          JSONB NOT NULL DEFAULT '[]',
  sample_messaging  TEXT,
  qdrant_point_id   UUID,
  model_used        VARCHAR(100),
  confidence_score  FLOAT,
  generated_at      TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at        TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_icp_company ON icp_profiles(company_id, is_current);

-- ============================================================
-- CAMPAIGN CONTEXT
-- ============================================================
CREATE TABLE IF NOT EXISTS campaign_context (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  version         INTEGER NOT NULL DEFAULT 1,
  is_current      BOOLEAN NOT NULL DEFAULT TRUE,
  brand_voice     JSONB NOT NULL DEFAULT '{}',
  key_messages    JSONB NOT NULL DEFAULT '[]',
  pain_narratives JSONB NOT NULL DEFAULT '[]',
  proof_points    JSONB NOT NULL DEFAULT '[]',
  cta_variants    JSONB NOT NULL DEFAULT '[]',
  channel_context JSONB NOT NULL DEFAULT '{}',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_campaign_context_company ON campaign_context(company_id, is_current);

-- ============================================================
-- AI OUTPUTS (immutable audit log)
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_outputs (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id         UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id        UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  output_type       VARCHAR(100) NOT NULL,
  model_used        VARCHAR(100) NOT NULL,
  prompt_tokens     INTEGER,
  completion_tokens INTEGER,
  raw_response      JSONB NOT NULL DEFAULT '{}',
  parsed_output     JSONB NOT NULL DEFAULT '{}',
  is_valid          BOOLEAN NOT NULL DEFAULT TRUE,
  validation_error  TEXT,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ai_outputs_company ON ai_outputs(company_id, output_type);
CREATE INDEX IF NOT EXISTS idx_ai_outputs_type    ON ai_outputs(output_type, created_at DESC);

-- ============================================================
-- EMBEDDINGS METADATA
-- ============================================================
CREATE TABLE IF NOT EXISTS embeddings_metadata (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id         UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id        UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  source_type       VARCHAR(100) NOT NULL,
  source_id         UUID NOT NULL,
  qdrant_collection VARCHAR(100) NOT NULL,
  qdrant_point_id   UUID NOT NULL,
  model_used        VARCHAR(100),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_embeddings_point
  ON embeddings_metadata(qdrant_collection, qdrant_point_id);

-- ============================================================
-- WORKFLOW RUNS
-- ============================================================
CREATE TABLE IF NOT EXISTS workflow_runs (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id       UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id      UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  temporal_run_id VARCHAR(255),
  workflow_type   VARCHAR(100) NOT NULL DEFAULT 'business_onboarding',
  status          workflow_status NOT NULL DEFAULT 'pending',
  progress        JSONB NOT NULL DEFAULT '{"steps_total":8,"steps_done":0,"current_step":"intake","percent":0}',
  error_detail    TEXT,
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_workflow_company  ON workflow_runs(company_id);
CREATE INDEX IF NOT EXISTS idx_workflow_temporal ON workflow_runs(temporal_run_id);
CREATE INDEX IF NOT EXISTS idx_workflow_status   ON workflow_runs(status);

-- ============================================================
-- EVENTS LOG
-- ============================================================
CREATE TABLE IF NOT EXISTS events_log (
  id          BIGSERIAL PRIMARY KEY,
  tenant_id   UUID REFERENCES tenants(id) ON DELETE SET NULL,
  company_id  UUID REFERENCES companies(id) ON DELETE SET NULL,
  run_id      UUID,
  event_type  VARCHAR(100) NOT NULL,
  severity    VARCHAR(20) NOT NULL DEFAULT 'info',
  payload     JSONB NOT NULL DEFAULT '{}',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_events_company ON events_log(company_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_type    ON events_log(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_run     ON events_log(run_id);
