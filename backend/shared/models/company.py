import uuid
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Boolean, Text, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.models.base import Base, TimestampMixin, UUIDPrimaryKey
import enum


class WorkflowStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    scraping = "scraping"
    cleaning = "cleaning"
    extracting = "extracting"
    positioning = "positioning"
    icp_generating = "icp_generating"
    embedding = "embedding"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class ScrapeStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class Company(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "companies"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255))
    website_url: Mapped[str | None] = mapped_column(String(1024))
    linkedin_url: Mapped[str | None] = mapped_column(String(1024))
    crunchbase_url: Mapped[str | None] = mapped_column(String(1024))
    description: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(255))
    sub_industry: Mapped[str | None] = mapped_column(String(255))
    business_model: Mapped[str | None] = mapped_column(String(100))
    company_size: Mapped[str | None] = mapped_column(String(50))
    employee_count: Mapped[int | None] = mapped_column(Integer)
    founded_year: Mapped[int | None] = mapped_column(Integer)
    headquarters_city: Mapped[str | None] = mapped_column(String(255))
    headquarters_country: Mapped[str | None] = mapped_column(String(100))
    geography: Mapped[str | None] = mapped_column(String(255))
    funding_stage: Mapped[str | None] = mapped_column(String(100))
    total_funding_usd: Mapped[int | None] = mapped_column(BigInteger)
    annual_revenue_range: Mapped[str | None] = mapped_column(String(100))
    pricing_range: Mapped[str | None] = mapped_column(String(100))
    tech_stack: Mapped[dict] = mapped_column(JSONB, default=list)
    social_profiles: Mapped[dict] = mapped_column(JSONB, default=dict)
    intake_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    enriched_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    intelligence_status: Mapped[WorkflowStatus] = mapped_column(
        SAEnum(WorkflowStatus, name="workflow_status", create_type=False), default=WorkflowStatus.pending
    )
    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    contacts: Mapped[list["Contact"]] = relationship(back_populates="company", lazy="select")
    products: Mapped[list["Product"]] = relationship(back_populates="company", lazy="select")


class Contact(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "contacts"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    linkedin_url: Mapped[str | None] = mapped_column(String(1024))
    job_title: Mapped[str | None] = mapped_column(String(255))
    seniority: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    is_founder: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    contact_type: Mapped[str] = mapped_column(String(50), default="general")
    raw_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    company: Mapped["Company"] = relationship(back_populates="contacts")


class Product(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "products"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    product_type: Mapped[str | None] = mapped_column(String(100))
    pricing_model: Mapped[str | None] = mapped_column(String(100))
    pricing_range: Mapped[str | None] = mapped_column(String(100))
    pricing_tiers: Mapped[list] = mapped_column(JSONB, default=list)
    core_features: Mapped[list] = mapped_column(JSONB, default=list)
    differentiators: Mapped[list] = mapped_column(JSONB, default=list)
    problems_solved: Mapped[list] = mapped_column(JSONB, default=list)
    target_use_cases: Mapped[list] = mapped_column(JSONB, default=list)
    target_market: Mapped[str | None] = mapped_column(Text)
    goals: Mapped[list] = mapped_column(JSONB, default=list)
    raw_intake: Mapped[dict] = mapped_column(JSONB, default=dict)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    company: Mapped["Company"] = relationship(back_populates="products")


class ScrapedPage(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "scraped_pages"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    apify_run_id: Mapped[str | None] = mapped_column(String(255))
    apify_actor_id: Mapped[str | None] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    status: Mapped[ScrapeStatus] = mapped_column(SAEnum(ScrapeStatus, name="scrape_status", create_type=False), default=ScrapeStatus.pending)
    raw_content: Mapped[str | None] = mapped_column(Text)
    structured_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    content_hash: Mapped[str | None] = mapped_column(String(64))
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error_detail: Mapped[str | None] = mapped_column(Text)


class WorkflowRun(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "workflow_runs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    temporal_run_id: Mapped[str | None] = mapped_column(String(255))
    workflow_type: Mapped[str] = mapped_column(String(100), default="business_onboarding")
    status: Mapped[WorkflowStatus] = mapped_column(SAEnum(WorkflowStatus, name="workflow_status", create_type=False), default=WorkflowStatus.pending)
    progress: Mapped[dict] = mapped_column(
        JSONB,
        default=lambda: {"steps_total": 8, "steps_done": 0, "current_step": "intake", "percent": 0},
    )
    error_detail: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
