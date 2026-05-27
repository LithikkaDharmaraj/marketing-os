/** Lightweight competitor summary — name + optional positioning note */
export interface CompetitorSummary {
  name: string;
  domain?: string;
  positioning?: string;
  key_differentiator?: string;
}

export interface ProductIntelligence {
  product_name: string;
  product_description: string;
  main_features: string[];
  main_problem_solved: string;
  target_industry: string;
  target_company_size: string;
  deployment_model: string;
  use_cases: string[];
  pricing_signals: string[];
}

export interface BusinessProfile {
  company_name: string;
  domain: string;
  industry: string;
  sub_industry: string;
  business_model: string;
  company_stage: string;
  value_proposition: string;
  core_product_categories: string[];
  target_segments: string[];
  geographies: string[];
  company_size_range: string;
  funding_stage: string;
  technology_indicators: string[];
  growth_signals: string[];
  market_position: string;
  competitive_landscape: CompetitorSummary[];
  key_differentiators: string[];
  pricing_model: string;
  product_intelligence?: ProductIntelligence;
  confidence_score: number;
}
