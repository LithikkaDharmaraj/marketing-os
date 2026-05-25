from pydantic import BaseModel, Field


class Firmographics(BaseModel):
    industries: list[str] = Field(default_factory=list)
    sub_industries: list[str] = Field(default_factory=list)
    company_sizes: list[str] = Field(default_factory=list, description="e.g. 500-5000 employees")
    revenue_ranges: list[str] = Field(default_factory=list)
    geographies: list[str] = Field(default_factory=list)
    funding_stages: list[str] = Field(default_factory=list)
    tech_stack_signals: list[str] = Field(default_factory=list)
    business_models: list[str] = Field(default_factory=list)


class Psychographics(BaseModel):
    goals: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    decision_style: str = ""
    success_metrics: list[str] = Field(default_factory=list)


class PainPoint(BaseModel):
    pain: str
    severity: str = "medium"
    current_solution: str = ""
    cost_of_inaction: str = ""


class ICPProfileSchema(BaseModel):
    profile_name: str = Field(description="e.g. Enterprise Compliance Head — Indian Private Bank")
    firmographics: Firmographics
    psychographics: Psychographics
    job_titles: list[str] = Field(default_factory=list)
    seniority_levels: list[str] = Field(default_factory=list, description="Director, VP, C-Suite, etc.")
    departments: list[str] = Field(default_factory=list)
    pain_points: list[PainPoint] = Field(default_factory=list)
    buying_triggers: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list, description="Where they consume content")
    decision_makers: list[str] = Field(default_factory=list, description="Other stakeholders in deal")
    sample_messaging: str = Field(default="", description="Example outreach message for this persona")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)


class ICPGenerationResponse(BaseModel):
    profiles: list[ICPProfileSchema]
