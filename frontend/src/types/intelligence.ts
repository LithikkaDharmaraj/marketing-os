/** Full competitor profile — used for both AI-discovered and user-suggested competitors */
export interface DiscoveredCompetitor {
  name: string;
  website: string;
  category: string;
  positioning: string;
  target_audience: string[];
  pricing_model: string;
  core_features: string[];
  strengths: string[];
  weaknesses: string[];
  messaging_style: string;
  differentiators: string[];
  differentiation_opportunities: string[];
  market_segment: string;
  estimated_company_size: string;
  competitor_type: "direct" | "indirect" | "emerging";
  competitiveness_level: string;
  confidence_score: number;
  similarity_score: number;
  discovery_source: "ai_reasoning" | "google_search" | "vector_similarity" | "user_provided";
  discovered_by_ai: boolean;
  user_provided: boolean;
}

/** Legacy alias kept for backward compat with existing competitor_profiles data */
export interface CompetitorSummary {
  name: string;
  domain: string;
  positioning: string;
  key_differentiator: string;
  target_audience?: string;
  strengths?: string[];
  differentiation_opportunities?: string[];
  competitiveness_level?: string;
  // New fields present in enriched profiles (same shape as DiscoveredCompetitor)
  website?: string;
  core_features?: string[];
  weaknesses?: string[];
  competitor_type?: string;
  discovery_source?: string;
  similarity_score?: number;
  confidence_score?: number;
  user_provided?: boolean;
  discovered_by_ai?: boolean;
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
  confidence_score: number;
}
