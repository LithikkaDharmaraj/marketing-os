from pydantic import BaseModel, Field


class ProductIntelligence(BaseModel):
    """Structured product intelligence — the core driver for all downstream GTM outputs."""
    product_name: str = Field(default="", description="The primary product or service name")
    product_description: str = Field(default="", description="2-3 sentence product description")
    main_features: list[str] = Field(default_factory=list, description="Top 5-7 core features")
    main_problem_solved: str = Field(default="", description="The #1 problem the product solves")
    target_industry: str = Field(default="", description="Primary target industry vertical")
    target_company_size: str = Field(default="", description="Ideal company size e.g. 100-5000 employees, Enterprise")
    deployment_model: str = Field(default="", description="Cloud SaaS, On-premise, Hybrid, API")
    use_cases: list[str] = Field(default_factory=list, description="Top 3-5 use cases")
    pricing_signals: list[str] = Field(default_factory=list, description="Pricing tiers or signals found on website")


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
    product_intelligence: ProductIntelligence = Field(default_factory=ProductIntelligence, description="Structured product-level intelligence driving all GTM outputs")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
