from pydantic import BaseModel, Field


class TargetCompanySchema(BaseModel):
    name: str
    domain: str
    linkedin_url: str = ""
    industry: str = ""
    company_size: str = ""
    headquarters: str = ""
    why_they_match: str = ""
    icp_profile_name: str = ""
    pain_points_matched: list[str] = Field(default_factory=list)
    priority: str = "high"


class TargetCompanyDiscoveryResponse(BaseModel):
    companies: list[TargetCompanySchema]


class TargetContactSchema(BaseModel):
    company_name: str = ""
    company_domain: str = ""
    full_name: str = ""
    designation: str = ""
    department: str = ""
    seniority: str = ""
    linkedin_url: str = ""
    email: str = ""
    why_target: str = ""
    outreach_angle: str = ""
    priority: str = "high"


class TargetContactsForCompanyResponse(BaseModel):
    contacts: list[TargetContactSchema]
