import asyncio
import uuid
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.models.company import Company, ScrapedPage, WorkflowStatus
from shared.schemas.business_profile import (
    BusinessProfileSchema,
    DiscoveredCompetitor,
    CompetitorDiscoveryResponse,
)
from shared.utils.groq_client import call_groq_structured
from shared.config import get_settings
from services.intelligence_service.app.prompts.intelligence_prompts import (
    BUSINESS_INTELLIGENCE_SYSTEM,
    build_intelligence_prompt,
    COMPETITOR_DISCOVERY_SYSTEM,
    build_competitor_discovery_prompt,
    COMPETITOR_EXTRACTION_SYSTEM,
    build_competitor_prompt,
)

logger = logging.getLogger(__name__)


async def _search_qdrant_competitors(
    company_profile: BusinessProfileSchema,
    tenant_id: str,
    settings,
) -> list[dict]:
    """Search Qdrant for competitors similar to this company profile.

    Returns a (possibly empty) list of competitor dicts with discovery_source='vector_similarity'.
    Fails silently — competitor discovery continues via AI reasoning if this errors.
    """
    try:
        import httpx
        text = (
            f"{company_profile.industry} {company_profile.sub_industry} "
            f"{company_profile.value_proposition} "
            f"{' '.join(company_profile.target_segments)} "
            f"{' '.join(company_profile.core_product_categories)}"
        )
        embedding_url = f"http://embedding-service:{settings.embedding_service_port}/api/v1"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{embedding_url}/embedding/competitors/search",
                json={"query": text, "tenant_id": tenant_id, "limit": 5},
            )
            if resp.status_code != 200:
                return []
            results = resp.json().get("results", [])
        competitors = []
        for r in results:
            p = r.get("payload", {})
            if r.get("score", 0) < 0.65:
                continue
            competitors.append({
                **p.get("competitor_data", {}),
                "discovery_source": "vector_similarity",
                "similarity_score": round(r["score"], 3),
                "discovered_by_ai": True,
                "user_provided": False,
            })
        return competitors
    except Exception as e:
        logger.debug(f"Qdrant competitor search skipped: {e}")
        return []


async def _store_competitors_in_qdrant(
    competitors: list[dict],
    company_id: str,
    tenant_id: str,
    settings,
) -> None:
    """Embed and store discovered competitors in Qdrant for future similarity lookups."""
    if not competitors:
        return
    try:
        import httpx
        embedding_url = f"http://embedding-service:{settings.embedding_service_port}/api/v1"
        async with httpx.AsyncClient(timeout=30) as client:
            for c in competitors:
                await client.post(
                    f"{embedding_url}/embedding/competitors/upsert",
                    json={
                        "company_id": company_id,
                        "tenant_id": tenant_id,
                        "competitor_data": c,
                    },
                )
    except Exception as e:
        logger.debug(f"Qdrant competitor storage skipped: {e}")


async def _discover_competitors_with_ai(
    business_profile: BusinessProfileSchema,
    scraped_data: dict,
    user_provided_hints: list[str],
    qdrant_competitors: list[dict],
    settings,
) -> list[dict]:
    """Use Groq LLM to discover competitors based on business profile and market context.

    Already-found Qdrant competitors are excluded from the AI prompt to avoid duplicates.
    """
    # Build exclusion list: user hints + already-found from Qdrant
    qdrant_names = {c.get("name", "").lower() for c in qdrant_competitors}
    exclusion_hints = list(user_provided_hints)

    profile_dict = business_profile.model_dump()
    prompt = build_competitor_discovery_prompt(
        business_profile=profile_dict,
        scraped_data=scraped_data,
        user_provided_hints=exclusion_hints,
    )

    try:
        response = await call_groq_structured(
            system_prompt=COMPETITOR_DISCOVERY_SYSTEM,
            user_prompt=prompt,
            output_schema=CompetitorDiscoveryResponse,
            model=settings.groq_model_large,
            max_tokens=3500,
        )
        # Filter out any duplicates with Qdrant results
        ai_competitors = [
            c.model_dump()
            for c in response.competitors
            if c.name.lower() not in qdrant_names
        ]
        logger.info(f"AI discovered {len(ai_competitors)} competitors")
        return ai_competitors
    except Exception as e:
        logger.warning(f"AI competitor discovery failed: {e}")
        return []


async def _enrich_user_suggested_competitors(
    company_id: uuid.UUID,
    company_name: str,
    business_profile: BusinessProfileSchema,
    db: AsyncSession,
    settings,
) -> list[dict]:
    """Enrich user-provided competitors using their scraped website data.

    Returns DiscoveredCompetitor dicts with user_provided=True.
    """
    scraped_result = await db.execute(
        select(ScrapedPage).where(
            ScrapedPage.company_id == company_id,
            ScrapedPage.source_type == "competitor",
            ScrapedPage.status == "completed",
        )
    )
    competitor_pages = scraped_result.scalars().all()
    if not competitor_pages:
        return []

    company_context = (
        f"Industry: {business_profile.industry}\n"
        f"Value Proposition: {business_profile.value_proposition}\n"
        f"Target Segments: {', '.join(business_profile.target_segments)}\n"
        f"Business Model: {business_profile.business_model}"
    )

    async def _enrich_one(page: ScrapedPage) -> dict | None:
        if not page.structured_data:
            return None
        try:
            profile = await call_groq_structured(
                system_prompt=COMPETITOR_EXTRACTION_SYSTEM,
                user_prompt=build_competitor_prompt(
                    company_name=company_name,
                    competitor_url=page.source_url,
                    competitor_data=page.structured_data,
                    company_context=company_context,
                ),
                output_schema=DiscoveredCompetitor,
                model=settings.groq_model_fast,
            )
            result = profile.model_dump()
            # Enforce user_provided flags regardless of what Groq returned
            result["user_provided"] = True
            result["discovered_by_ai"] = False
            result["discovery_source"] = "user_provided"
            if not result.get("website"):
                result["website"] = page.source_url
            logger.info(f"User-suggested competitor enriched: {page.source_url}")
            return result
        except Exception as e:
            logger.warning(f"User-suggested competitor enrichment failed for {page.source_url}: {e}")
            return None

    results = await asyncio.gather(*[_enrich_one(p) for p in competitor_pages])
    return [r for r in results if r is not None]


async def extract_business_intelligence(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> BusinessProfileSchema:
    """Run AI extraction over all scraped data to produce a structured business profile."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    settings = get_settings()

    # ── Cache path: business profile already extracted ────────────────────
    if company.enriched_data.get("business_profile"):
        logger.info(f"Business profile cached for company {company_id}")
        profile = BusinessProfileSchema(**company.enriched_data["business_profile"])

        needs_ai_discovery = "ai_discovered_competitors" not in company.enriched_data
        needs_user_enrichment = "user_suggested_competitors" not in company.enriched_data

        if needs_ai_discovery or needs_user_enrichment:
            scraped_result = await db.execute(
                select(ScrapedPage).where(
                    ScrapedPage.company_id == company_id,
                    ScrapedPage.status == "completed",
                )
            )
            pages = scraped_result.scalars().all()
            scraped_data = {}
            for p in pages:
                if p.source_type != "competitor":
                    scraped_data[p.source_type] = p.structured_data

            updates: dict = {}
            if needs_ai_discovery:
                qdrant_hits = await _search_qdrant_competitors(profile, str(tenant_id), settings)
                user_hints = company.intake_data.get("competitors", [])
                ai_competitors = await _discover_competitors_with_ai(
                    profile, scraped_data, user_hints, qdrant_hits, settings
                )
                all_ai = qdrant_hits + ai_competitors
                updates["ai_discovered_competitors"] = all_ai
                await _store_competitors_in_qdrant(all_ai, str(company_id), str(tenant_id), settings)

            if needs_user_enrichment:
                user_competitors = await _enrich_user_suggested_competitors(
                    company_id, profile.company_name, profile, db, settings
                )
                updates["user_suggested_competitors"] = user_competitors

            if updates:
                company.enriched_data = {**company.enriched_data, **updates}
                await db.commit()
                logger.info(
                    f"Competitor discovery (post-cache): "
                    f"ai={len(updates.get('ai_discovered_competitors', []))} "
                    f"user={len(updates.get('user_suggested_competitors', []))}"
                )

        if company.intelligence_status == WorkflowStatus.queued:
            company.intelligence_status = WorkflowStatus.positioning
            await db.commit()
        return profile

    # ── Full extraction path ───────────────────────────────────────────────
    scraped_result = await db.execute(
        select(ScrapedPage).where(
            ScrapedPage.company_id == company_id,
            ScrapedPage.status == "completed",
        )
    )
    pages = scraped_result.scalars().all()

    # Build scraped_data dict (non-competitor pages)
    scraped_data: dict = {}
    for p in pages:
        if p.source_type != "competitor":
            scraped_data[p.source_type] = p.structured_data

    # Step 1: Extract main business profile
    user_prompt = build_intelligence_prompt(company.intake_data, scraped_data)
    profile = await call_groq_structured(
        system_prompt=BUSINESS_INTELLIGENCE_SYSTEM,
        user_prompt=user_prompt,
        output_schema=BusinessProfileSchema,
    )

    # Step 2: AI competitor discovery (parallel with user-suggested enrichment)
    user_hints: list[str] = company.intake_data.get("competitors", [])

    qdrant_hits = await _search_qdrant_competitors(profile, str(tenant_id), settings)

    ai_task = _discover_competitors_with_ai(
        profile, scraped_data, user_hints, qdrant_hits, settings
    )
    user_task = _enrich_user_suggested_competitors(
        company_id, profile.company_name, profile, db, settings
    )
    ai_competitors_raw, user_suggested = await asyncio.gather(ai_task, user_task)

    ai_discovered = qdrant_hits + ai_competitors_raw

    # Step 3: Store AI competitors in Qdrant for future similarity lookups
    await _store_competitors_in_qdrant(ai_discovered, str(company_id), str(tenant_id), settings)

    # Step 4: Persist everything
    company.industry = profile.industry or company.industry
    company.sub_industry = profile.sub_industry or company.sub_industry
    company.business_model = profile.business_model or company.business_model
    company.enriched_data = {
        **company.enriched_data,
        "business_profile": profile.model_dump(),
        "ai_discovered_competitors": ai_discovered,
        "user_suggested_competitors": user_suggested,
        # Legacy key kept for older frontend code that may still read it
        "competitor_profiles": ai_discovered,
        "extracted_at": datetime.utcnow().isoformat(),
    }
    company.intelligence_status = WorkflowStatus.positioning

    await db.commit()
    logger.info(
        f"Business intelligence extracted for company {company_id} — "
        f"ai_discovered={len(ai_discovered)} user_suggested={len(user_suggested)}"
    )
    return profile
