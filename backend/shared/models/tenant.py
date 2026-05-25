import uuid
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from shared.models.base import Base, TimestampMixin, UUIDPrimaryKey
import enum


class TenantPlan(str, enum.Enum):
    trial = "trial"
    starter = "starter"
    growth = "growth"
    enterprise = "enterprise"


class Tenant(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[TenantPlan] = mapped_column(
        SAEnum(TenantPlan, name="tenant_plan"), nullable=False, default=TenantPlan.trial
    )
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    usage_quota: Mapped[dict] = mapped_column(JSONB, default=dict)
    usage_current: Mapped[dict] = mapped_column(JSONB, default=dict)
