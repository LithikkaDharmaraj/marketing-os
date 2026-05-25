import uuid
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from shared.models.company import Company, WorkflowStatus
from shared.schemas.campaign_context import CampaignContextSchema, BrandVoice, PainNarrative, ProofPoint, ChannelContext
from shared.utils.groq_client import call_groq_structured

logger = logging.getLogger(__name__)

CAMPAIGN_CONTEXT_SYSTEM = """You are a B2B demand generation expert.
Generate reusable campaign context — brand voice, key messages, pain narratives, proof points, and CTAs —
based on the company's positioning and ICP profiles. This will be used to generate all future campaigns.
Output ONLY valid JSON."""


async def generate_campaign_context(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> CampaignContextSchema:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    business_profile = company.enriched_data.get("business_profile", {})
    positioning_profile = company.enriched_data.get("positioning_profile", {})
    icp_profiles = company.enriched_data.get("icp_profiles", [])

    user_prompt = f"""Generate campaign context for this company.

COMPANY: {business_profile.get("company_name", "")}
VALUE PROPOSITION: {business_profile.get("value_proposition", "")}
CORE POSITIONING: {positioning_profile.get("core_positioning", {}).get("statement", "")}
MESSAGING ANGLES: {positioning_profile.get("messaging_angles", [])[:3]}
EMOTIONAL TRIGGERS: {positioning_profile.get("emotional_triggers", [])[:3]}

ICP PROFILES:
{json.dumps(icp_profiles[:2], indent=2)[:2000]}

Generate CampaignContextSchema with:
- brand_voice (tone, style, personality traits, things to avoid)
- key_messages (5-7 core messages)
- pain_narratives (one per ICP — specific, emotional narratives)
- proof_points (data-backed claims)
- cta_variants (5 CTAs for different funnel stages)
- channel_context (email, linkedin, ads, landing_page specifics)
- hooks (5 attention-grabbing openers)"""

    context = await call_groq_structured(
        system_prompt=CAMPAIGN_CONTEXT_SYSTEM,
        user_prompt=user_prompt,
        output_schema=CampaignContextSchema,
    )

    await db.execute(
        text("""
            UPDATE campaign_context SET is_current = false WHERE company_id = :cid
        """),
        {"cid": str(company_id)},
    )
    await db.execute(
        text("""
            INSERT INTO campaign_context (
                tenant_id, company_id, is_current, brand_voice, key_messages,
                pain_narratives, proof_points, cta_variants, channel_context
            ) VALUES (
                :tenant_id, :company_id, true,
                CAST(:brand_voice AS jsonb), CAST(:key_messages AS jsonb),
                CAST(:pain_narratives AS jsonb), CAST(:proof_points AS jsonb),
                CAST(:cta_variants AS jsonb), CAST(:channel_context AS jsonb)
            )
        """),
        {
            "tenant_id": str(tenant_id),
            "company_id": str(company_id),
            "brand_voice": json.dumps(context.brand_voice.model_dump()),
            "key_messages": json.dumps(context.key_messages),
            "pain_narratives": json.dumps([p.model_dump() for p in context.pain_narratives]),
            "proof_points": json.dumps([p.model_dump() for p in context.proof_points]),
            "cta_variants": json.dumps(context.cta_variants),
            "channel_context": json.dumps(context.channel_context.model_dump()),
        },
    )

    company.intelligence_status = WorkflowStatus.completed
    await db.commit()
    logger.info(f"Campaign context generated for company {company_id}")
    return context
