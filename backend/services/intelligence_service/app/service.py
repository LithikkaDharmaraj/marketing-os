import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.models.company import Company, ScrapedPage, WorkflowStatus
from shared.schemas.business_profile import BusinessProfileSchema
from shared.utils.groq_client import call_groq_structured
from shared.config import get_settings
from services.intelligence_service.app.prompts.intelligence_prompts import (
    BUSINESS_INTELLIGENCE_SYSTEM,
    build_intelligence_prompt,
)

logger = logging.getLogger(__name__)


async def extract_business_intelligence(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> BusinessProfileSchema:
    """Run AI extraction over scraped data to produce a structured business + product profile."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    settings = get_settings()

    # Cache: business profile already extracted
    if company.enriched_data.get("business_profile"):
        logger.info(f"Business profile cached for company {company_id}")
        profile = BusinessProfileSchema(**company.enriched_data["business_profile"])
        if company.intelligence_status == WorkflowStatus.queued:
            company.intelligence_status = WorkflowStatus.positioning
            await db.commit()
        return profile

    # Load scraped pages (skip competitor pages — not the focus)
    scraped_result = await db.execute(
        select(ScrapedPage).where(
            ScrapedPage.company_id == company_id,
            ScrapedPage.status == "completed",
        )
    )
    pages = scraped_result.scalars().all()
    scraped_data = {p.source_type: p.structured_data for p in pages if p.source_type != "competitor"}

    # Extract business + product intelligence in one LLM call
    user_prompt = build_intelligence_prompt(company.intake_data, scraped_data)
    profile = await call_groq_structured(
        system_prompt=BUSINESS_INTELLIGENCE_SYSTEM,
        user_prompt=user_prompt,
        output_schema=BusinessProfileSchema,
        model=settings.groq_model_large,
    )

    # Backfill product_intelligence from intake hints where AI left fields blank
    pi = profile.product_intelligence
    intake = company.intake_data
    if not pi.target_industry and intake.get("target_industry"):
        val = intake["target_industry"]
        pi.target_industry = ", ".join(val) if isinstance(val, list) else val
    if not pi.target_company_size and intake.get("target_company_size"):
        pi.target_company_size = intake["target_company_size"]
    if not pi.main_problem_solved and intake.get("main_problem_solved"):
        pi.main_problem_solved = intake["main_problem_solved"]
    if not pi.product_description and intake.get("product_description"):
        pi.product_description = intake["product_description"]
    if not pi.use_cases and intake.get("target_departments"):
        pi.use_cases = [f"Used by {d} teams" for d in intake["target_departments"][:3]]

    # Persist
    company.industry = profile.industry or company.industry
    company.sub_industry = profile.sub_industry or company.sub_industry
    company.business_model = profile.business_model or company.business_model
    company.enriched_data = {
        **company.enriched_data,
        "business_profile": profile.model_dump(),
        "extracted_at": datetime.utcnow().isoformat(),
    }
    company.intelligence_status = WorkflowStatus.positioning

    # Sync product_intelligence into the Product row
    if pi and (pi.product_name or pi.main_features):
        from shared.models.company import Product
        product_result = await db.execute(select(Product).where(Product.company_id == company_id))
        product = product_result.scalars().first()
        if product:
            if pi.product_name:
                product.name = pi.product_name
            if pi.product_description:
                product.description = pi.product_description
            if pi.main_features:
                product.core_features = pi.main_features
            if pi.main_problem_solved:
                product.problems_solved = [pi.main_problem_solved]
            if pi.target_company_size:
                product.target_market = (
                    f"{pi.target_industry} — {pi.target_company_size}".strip(" —")
                    if pi.target_industry else pi.target_company_size
                )
            if pi.use_cases:
                product.target_use_cases = pi.use_cases

    await db.commit()
    logger.info(f"Business intelligence extracted for company {company_id}")
    return profile
