from pydantic import BaseModel, field_validator
from typing import Optional
import uuid


class ContactInput(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: str = "general"
    is_founder: bool = False
    is_primary: bool = False


class CompanyIntakeRequest(BaseModel):
    # Required core fields
    company_name: str
    website_url: str
    industry: str
    geography: str

    # AI-inferred (optional — scraped from website)
    sub_industry: Optional[str] = None
    company_size: Optional[str] = None
    business_model: Optional[str] = None
    annual_revenue_range: Optional[str] = None
    linkedin_url: Optional[str] = None
    crunchbase_url: Optional[str] = None
    additional_notes: Optional[str] = None

    # Product (optional — AI extracts from website)
    product_type: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    services_products: Optional[str] = None
    target_market: Optional[str] = None
    pricing_range: Optional[str] = None
    core_features: list[str] = []
    differentiators: list[str] = []
    problems_solved: list[str] = []

    # Competitors (all optional)
    competitors: list[str] = []

    # Goals
    goals: list[str] = []
    target_segments: list[str] = []

    # Contacts
    contacts: list[ContactInput] = []

    # Tenant context
    tenant_id: uuid.UUID

    @field_validator("website_url")
    @classmethod
    def clean_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v


class CompanyIntakeResponse(BaseModel):
    company_id: uuid.UUID
    workflow_run_id: uuid.UUID
    status: str
    message: str


class IntakeStatusResponse(BaseModel):
    company_id: uuid.UUID
    workflow_run_id: uuid.UUID
    status: str
    progress: dict
    company_name: str
