export interface ContactInput {
  full_name?: string;
  email?: string;
  contact_type: string;
  is_founder: boolean;
  is_primary: boolean;
}

export interface IntakeFormData {
  // Step 1: Company (required)
  company_name: string;
  website_url: string;
  industry: string;
  geography: string;

  // Step 1: Company (AI-inferred, optional)
  sub_industry?: string;
  linkedin_url?: string;
  additional_notes?: string;

  // Step 2: Product
  product_description?: string;
  main_problem_solved?: string;
  target_industry?: string[];
  target_company_size?: string;
  target_departments?: string[];
  pricing_range?: string;

  // Step 3: Competitors (all optional)
  competitors: string[];

  // Step 4: Contacts
  contacts: ContactInput[];

  // Meta
  tenant_id: string;
}

export interface IntakeResponse {
  company_id: string;
  workflow_run_id: string;
  status: string;
  message: string;
}
