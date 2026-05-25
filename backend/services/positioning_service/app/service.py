import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.models.company import Company, ScrapedPage, WorkflowStatus
from shared.schemas.positioning_profile import PositioningProfileSchema
from shared.utils.groq_client import call_groq_structured
from services.positioning_service.app.prompts.positioning_prompts import (
    POSITIONING_SYSTEM,
    build_positioning_prompt,
)

logger = logging.getLogger(__name__)

POSITIONING_TABLE = "positioning_profiles"


async def generate_positioning(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> PositioningProfileSchema:
    """Generate positioning profile using AI reasoning over business profile + competitive data."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    business_profile = company.enriched_data.get("business_profile", {})
    if not business_profile:
        raise ValueError(f"Business profile not yet extracted for company {company_id}")

    # Return cached result if already generated
    if company.enriched_data.get("positioning_profile"):
        logger.info(f"Positioning profile already exists for company {company_id}, returning cached")
        if company.intelligence_status not in (WorkflowStatus.icp_generating, WorkflowStatus.embedding, WorkflowStatus.completed):
            company.intelligence_status = WorkflowStatus.icp_generating
            await db.commit()
        return PositioningProfileSchema(**company.enriched_data["positioning_profile"])

    # Aggregate scraped data
    scraped_result = await db.execute(
        select(ScrapedPage).where(
            ScrapedPage.company_id == company_id,
            ScrapedPage.status == "completed",
        )
    )
    pages = scraped_result.scalars().all()
    scraped_data = {p.source_type: p.structured_data for p in pages}

    user_prompt = build_positioning_prompt(business_profile, scraped_data, company.intake_data)

    positioning = await call_groq_structured(
        system_prompt=POSITIONING_SYSTEM,
        user_prompt=user_prompt,
        output_schema=PositioningProfileSchema,
    )

    import json
    from sqlalchemy import text

    await db.execute(
        text("UPDATE positioning_profiles SET is_current = false WHERE company_id = :company_id AND is_current = true"),
        {"company_id": str(company_id)},
    )

    await db.execute(
        text("""
            INSERT INTO positioning_profiles (
                tenant_id, company_id, is_current, status,
                core_positioning, segment_positioning, messaging_angles,
                emotional_triggers, competitive_moats, value_propositions,
                objection_handling, model_used, confidence_score, generated_at
            ) VALUES (
                :tenant_id, :company_id, true, 'completed',
                CAST(:core_positioning AS jsonb), CAST(:segment_positioning AS jsonb),
                CAST(:messaging_angles AS jsonb), CAST(:emotional_triggers AS jsonb),
                CAST(:competitive_moats AS jsonb), CAST(:value_propositions AS jsonb),
                CAST(:objection_handling AS jsonb), :model_used, :confidence_score, NOW()
            )
        """),
        {
            "tenant_id": str(tenant_id),
            "company_id": str(company_id),
            "core_positioning": json.dumps(positioning.core_positioning.model_dump()),
            "segment_positioning": json.dumps([s.model_dump() for s in positioning.segment_positioning]),
            "messaging_angles": json.dumps([m.model_dump() for m in positioning.messaging_angles]),
            "emotional_triggers": json.dumps([e.model_dump() for e in positioning.emotional_triggers]),
            "competitive_moats": json.dumps(positioning.competitive_moats),
            "value_propositions": json.dumps(positioning.value_propositions),
            "objection_handling": json.dumps([o.model_dump() for o in positioning.objection_handling]),
            "model_used": "llama-3.3-70b-versatile",
            "confidence_score": positioning.confidence_score,
        },
    )

    company.intelligence_status = WorkflowStatus.icp_generating
    company.enriched_data = {
        **company.enriched_data,
        "positioning_profile": positioning.model_dump(),
    }
    await db.commit()

    logger.info(f"Positioning generated for company {company_id}")
    return positioning
