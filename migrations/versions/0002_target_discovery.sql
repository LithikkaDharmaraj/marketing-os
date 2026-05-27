-- Marketing OS — Target Discovery Migration
-- Run via: make migrate2

-- Add new workflow statuses
ALTER TYPE workflow_status ADD VALUE IF NOT EXISTS 'target_discovering';

-- ============================================================
-- TARGET COMPANIES
-- ============================================================
CREATE TABLE IF NOT EXISTS target_companies (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name                VARCHAR(255) NOT NULL,
  domain              VARCHAR(255),
  linkedin_url        VARCHAR(1024),
  industry            VARCHAR(255),
  company_size        VARCHAR(100),
  headquarters        VARCHAR(255),
  why_they_match      TEXT,
  icp_profile_name    VARCHAR(255),
  pain_points_matched JSONB NOT NULL DEFAULT '[]',
  priority            VARCHAR(20)  NOT NULL DEFAULT 'high',
  scraped_data        JSONB NOT NULL DEFAULT '{}',
  created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_target_companies_company_id ON target_companies(company_id);

-- ============================================================
-- TARGET CONTACTS
-- ============================================================
CREATE TABLE IF NOT EXISTS target_contacts (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  target_company_id   UUID REFERENCES target_companies(id) ON DELETE CASCADE,
  company_name        VARCHAR(255),
  full_name           VARCHAR(255),
  designation         VARCHAR(255),
  department          VARCHAR(255),
  seniority           VARCHAR(100),
  linkedin_url        VARCHAR(1024),
  email               VARCHAR(255),
  why_target          TEXT,
  outreach_angle      TEXT,
  priority            VARCHAR(20) NOT NULL DEFAULT 'high',
  scraped_data        JSONB NOT NULL DEFAULT '{}',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_target_contacts_company_id        ON target_contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_target_contacts_target_company_id ON target_contacts(target_company_id);
