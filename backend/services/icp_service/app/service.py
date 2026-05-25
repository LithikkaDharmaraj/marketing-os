import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from shared.models.company import Company, WorkflowStatus
from shared.schemas.icp_profile import ICPGenerationResponse, ICPProfileSchema
from shared.utils.groq_client import call_groq_structured
from shared.config import get_settings
from services.icp_service.app.prompts.icp_prompts import ICP_SYSTEM, build_icp_prompt

settings = get_settings()

logger = logging.getLogger(__name__)


async def generate_icps(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[ICPProfileSchema]:
    """Generate 2-4 ICP profiles using AI and persist to database."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    business_profile = company.enriched_data.get("business_profile", {})
    positioning_profile = company.enriched_data.get("positioning_profile", {})

    if not business_profile:
        raise ValueError("Business profile required before ICP generation")

    # Return cached result if already generated
    if company.enriched_data.get("icp_profiles"):
        logger.info(f"ICP profiles already exist for company {company_id}, returning cached")
        if company.intelligence_status not in (WorkflowStatus.embedding, WorkflowStatus.completed):
            company.intelligence_status = WorkflowStatus.embedding
            await db.commit()
        return [ICPProfileSchema(**p) for p in company.enriched_data["icp_profiles"]]

    user_prompt = build_icp_prompt(business_profile, positioning_profile, company.intake_data)

    response = await call_groq_structured(
        system_prompt=ICP_SYSTEM,
        user_prompt=user_prompt,
        output_schema=ICPGenerationResponse,
        model=settings.groq_model_fast,
        max_tokens=3500,
    )

    # Mark old ICPs as not current
    await db.execute(
        text("UPDATE icp_profiles SET is_current = false WHERE company_id = :cid"),
        {"cid": str(company_id)},
    )

    # Persist each ICP
    for icp in response.profiles:
        await db.execute(
            text("""
                INSERT INTO icp_profiles (
                    tenant_id, company_id, profile_name, is_current,
                    firmographics, psychographics, job_titles, seniority_levels,
                    departments, buying_triggers, pain_points, objections,
                    channels, sample_messaging, model_used, confidence_score, generated_at
                ) VALUES (
                    :tenant_id, :company_id, :profile_name, true,
                    CAST(:firmographics AS jsonb), CAST(:psychographics AS jsonb), CAST(:job_titles AS jsonb),
                    CAST(:seniority_levels AS jsonb), CAST(:departments AS jsonb), CAST(:buying_triggers AS jsonb),
                    CAST(:pain_points AS jsonb), CAST(:objections AS jsonb), CAST(:channels AS jsonb),
                    :sample_messaging, :model_used, :confidence_score, NOW()
                )
            """),
            {
                "tenant_id": str(tenant_id),
                "company_id": str(company_id),
                "profile_name": icp.profile_name,
                "firmographics": json.dumps(icp.firmographics.model_dump()),
                "psychographics": json.dumps(icp.psychographics.model_dump()),
                "job_titles": json.dumps(icp.job_titles),
                "seniority_levels": json.dumps(icp.seniority_levels),
                "departments": json.dumps(icp.departments),
                "buying_triggers": json.dumps(icp.buying_triggers),
                "pain_points": json.dumps([p.model_dump() for p in icp.pain_points]),
                "objections": json.dumps(icp.objections),
                "channels": json.dumps(icp.channels),
                "sample_messaging": icp.sample_messaging,
                "model_used": "llama-3.3-70b-versatile",
                "confidence_score": icp.confidence_score,
            },
        )

    company.intelligence_status = WorkflowStatus.embedding
    company.enriched_data = {
        **company.enriched_data,
        "icp_profiles": [icp.model_dump() for icp in response.profiles],
    }
    await db.commit()

    logger.info(f"Generated {len(response.profiles)} ICP profiles for company {company_id}")
    return response.profiles
