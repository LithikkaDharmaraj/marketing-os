from pydantic import BaseModel, Field


class CompetitorSummary(BaseModel):
    """Lightweight summary kept for backward compat in BusinessProfile.competitive_landscape."""
    name: str
    domain: str = ""
    positioning: str = ""
    key_differentiator: str = ""
    target_audience: str = ""
    strengths: list[str] = Field(default_factory=list)
    differentiation_opportunities: list[str] = Field(default_factory=list)
    competitiveness_level: str = ""


class DiscoveredCompetitor(BaseModel):
    """Full competitor profile used for both AI-discovered and user-suggested competitors."""
    name: str
    website: str = ""
    category: str = ""
    positioning: str = ""
    target_audience: list[str] = Field(default_factory=list)
    pricing_model: str = ""
    core_features: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list, description="Relative weaknesses vs our company")
    messaging_style: str = ""
    differentiators: list[str] = Field(default_factory=list, description="How they differentiate from our company")
    differentiation_opportunities: list[str] = Field(default_factory=list, description="Gaps our company can exploit")
    market_segment: str = ""
    estimated_company_size: str = ""
    competitor_type: str = Field(default="direct", description="direct | indirect | emerging")
    competitiveness_level: str = Field(
        default="",
        description="Highly Competitive | Moderately Competitive | Less Competitive",
    )
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)
    similarity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    discovery_source: str = Field(
        default="ai_reasoning",
        description="ai_reasoning | google_search | vector_similarity | user_provided",
    )
    discovered_by_ai: bool = True
    user_provided: bool = False


class CompetitorDiscoveryResponse(BaseModel):
    """Groq output schema for AI competitor discovery."""
    competitors: list[DiscoveredCompetitor]


class BusinessProfileSchema(BaseModel):
    company_name: str = Field(description="Legal company name")
    domain: str = Field(default="", description="Primary domain e.g. lendkraft.ai")
    industry: str = Field(description="Primary industry e.g. FinTech")
    sub_industry: str = Field(default="", description="Sub-category e.g. RegTech / AI Compliance")
    business_model: str = Field(description="B2B, B2C, B2B2C, marketplace, etc.")
    company_stage: str = Field(default="", description="Startup, Growth, Enterprise")
    value_proposition: str = Field(description="One-sentence core value prop")
    core_product_categories: list[str] = Field(default_factory=list)
    target_segments: list[str] = Field(default_factory=list, description="Primary buyer segments")
    geographies: list[str] = Field(default_factory=list)
    company_size_range: str = Field(default="", description="e.g. 50-200 employees")
    funding_stage: str = Field(default="", description="Bootstrap, Seed, Series A, etc.")
    technology_indicators: list[str] = Field(default_factory=list)
    growth_signals: list[str] = Field(default_factory=list, description="Hiring, funding, expansion signals")
    market_position: str = Field(default="", description="Category leader, challenger, niche, etc.")
    competitive_landscape: list[CompetitorSummary] = Field(default_factory=list)
    key_differentiators: list[str] = Field(default_factory=list)
    pricing_model: str = Field(default="", description="Subscription, usage, freemium, etc.")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
