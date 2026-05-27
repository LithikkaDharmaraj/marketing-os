import asyncio
import re
import uuid
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from shared.utils.db import AsyncSessionLocal
from shared.models.company import Company
from shared.schemas.target_discovery import (
    TargetCompanySchema,
    TargetCompanyDiscoveryResponse,
    TargetContactSchema,
    TargetContactsForCompanyResponse,
)
from shared.utils.groq_client import call_groq_structured
from shared.config import get_settings as _get_settings
_settings = _get_settings()

logger = logging.getLogger(__name__)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _parse_linkedin_snippet(title: str, description: str) -> tuple[str, str, str]:
    """
    Parse name, designation, and LinkedIn URL hint from Google Search snippet.
    LinkedIn titles look like: "John Smith - VP Engineering at Myntra | LinkedIn"
    or:                         "John Smith · VP of Sales · Myntra"
    """
    name, designation = "", ""

    # Clean up
    title = title.replace(" | LinkedIn", "").strip()

    if " - " in title:
        parts = title.split(" - ", 1)
        name = parts[0].strip()
        rest = parts[1]
        if " at " in rest:
            designation = rest.split(" at ")[0].strip()
        else:
            designation = rest.split("|")[0].strip()
    elif " · " in title:
        parts = title.split(" · ")
        name = parts[0].strip()
        if len(parts) > 1:
            designation = parts[1].strip()

    # Fallback: try description
    if not name and description:
        desc_parts = description.split("·")
        if desc_parts:
            name = desc_parts[0].strip()
        if len(desc_parts) > 1:
            designation = desc_parts[1].strip()

    return name, designation


def _extract_emails_from_text(text: str, domain: str) -> list[str]:
    all_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return list({e for e in all_emails if domain.split(".")[0] in e})[:5]


# ─── Step 1: Google Search → LinkedIn profile URLs + snippets ─────────────────

async def _google_search_linkedin_people(
    company_name: str,
    job_titles: list[str],
) -> list[dict]:
    """
    Search Google for LinkedIn profiles at the company.
    Returns list of {url, full_name, designation, snippet}.
    """
    from services.scraper_service.app.actors.base_actor import BaseApifyActor

    # Build role-targeted queries
    roles = list(set(job_titles))[:4]
    if roles:
        role_part = " OR ".join(f'"{r}"' for r in roles[:3])
    else:
        role_part = '"VP" OR "Director" OR "Head of" OR "CEO" OR "Founder"'

    query_lines = [
        f'site:linkedin.com/in "{company_name}" ({role_part})',
        f'site:linkedin.com/in "{company_name}" decision maker',
    ]
    queries = "\n".join(query_lines)

    class _LinkedInGoogleSearch(BaseApifyActor):
        actor_id = "apify~google-search-scraper"
        timeout_seconds = 90

        def build_input(self, **kwargs) -> dict:
            return {
                "queries": queries,
                "maxPagesPerQuery": 1,
                "resultsPerPage": 10,
                "languageCode": "en",
            }

        def normalize(self, raw_items: list[dict]) -> dict:
            results = []
            seen_urls = set()
            for item in raw_items:
                for r in item.get("organicResults", []):
                    url = r.get("url", "")
                    if "linkedin.com/in/" in url and url not in seen_urls:
                        seen_urls.add(url)
                        results.append({
                            "url": url.split("?")[0],
                            "title": r.get("title", ""),
                            "description": r.get("description", ""),
                        })
            return {"results": results[:8]}

    actor = _LinkedInGoogleSearch()
    try:
        result = await actor.run()
        raw = result.get("structured_data", {}).get("results", [])
    except Exception as e:
        logger.warning(f"Google LinkedIn search failed for {company_name}: {e}")
        return []

    logger.info(f"Google found {len(raw)} LinkedIn profile URLs for {company_name}")

    contacts = []
    for r in raw:
        name, designation = _parse_linkedin_snippet(r["title"], r["description"])
        if name:
            contacts.append({
                "full_name": name,
                "designation": designation,
                "linkedin_url": r["url"],
                "data_source": "google_search",
            })

    return contacts


# ─── Step 2: Scrape LinkedIn profiles for real detail ─────────────────────────

async def _scrape_linkedin_profiles(linkedin_urls: list[str]) -> list[dict]:
    """Scrape individual LinkedIn profiles via harvestapi."""
    from services.scraper_service.app.actors.linkedin_company_actor import LinkedInProfileActor

    if not linkedin_urls:
        return []

    actor = LinkedInProfileActor()
    try:
        result = await actor.run(profile_urls=linkedin_urls)
        profiles = result.get("structured_data", {}).get("profiles", [])
        logger.info(f"harvestapi scraped {len(profiles)} profiles from {len(linkedin_urls)} URLs")
        return profiles
    except Exception as e:
        logger.warning(f"LinkedIn profile scraping failed: {e}")
        return []


# ─── Step 3: Scrape company website team/about pages ─────────────────────────

async def _scrape_company_website(domain: str) -> dict:
    """
    Crawl common team/leadership pages on the company website.
    Returns {page_text, emails_found}.
    """
    from services.scraper_service.app.actors.base_actor import BaseApifyActor

    start_urls = [
        {"url": f"https://{domain}/about"},
        {"url": f"https://{domain}/team"},
        {"url": f"https://{domain}/leadership"},
        {"url": f"https://{domain}/about-us"},
    ]

    class _TeamPageCrawler(BaseApifyActor):
        actor_id = "apify~website-content-crawler"
        timeout_seconds = 120

        def build_input(self, **kwargs) -> dict:
            return {
                "startUrls": start_urls[:2],
                "maxCrawlPages": 4,
                "maxCrawlDepth": 1,
                "crawlerType": "cheerio",
                "saveFiles": False,
                "saveScreenshots": False,
            }

        def normalize(self, raw_items: list[dict]) -> dict:
            texts, emails = [], set()
            for item in raw_items:
                text = item.get("text", "") or item.get("markdown", "")
                if text:
                    texts.append(text[:3000])
                    for e in _extract_emails_from_text(text, domain):
                        emails.add(e)
            return {
                "page_text": "\n---\n".join(texts[:3]),
                "emails_found": list(emails)[:10],
            }

    actor = _TeamPageCrawler()
    try:
        result = await actor.run()
        data = result.get("structured_data", {})
        logger.info(f"Website crawl for {domain}: {len(data.get('emails_found', []))} emails found")
        return data
    except Exception as e:
        logger.warning(f"Website crawl failed for {domain}: {e}")
        return {}


# ─── Step 4: Groq enrichment ──────────────────────────────────────────────────

_CONTACT_SYSTEM = """You are a B2B sales intelligence expert.
Given a target company, ICP profiles, and any scraped data, generate precise outreach-ready contact records.
Output ONLY valid JSON matching TargetContactsForCompanyResponse."""


async def _groq_enrich_contacts(
    target_company: TargetCompanySchema,
    icp_profiles: list[dict],
    scraped_contacts: list[dict],
    website_data: dict,
    product_intelligence: dict | None = None,
) -> list[TargetContactSchema]:
    """
    Use scraped contacts as the base. Groq fills in outreach angles,
    infers missing fields, and adds 1-2 contacts from website data if available.
    """
    scraped_summary = ""
    if scraped_contacts:
        scraped_summary = f"\nREAL SCRAPED CONTACTS (use these names and titles exactly):\n{json.dumps(scraped_contacts[:5], indent=2)}"

    website_summary = ""
    if website_data.get("page_text"):
        website_summary = f"\nWEBSITE TEAM PAGE TEXT (extract any names/roles found):\n{website_data['page_text'][:1000]}"
    if website_data.get("emails_found"):
        website_summary += f"\nEMAILS FOUND ON WEBSITE: {website_data['emails_found']}"

    icp_roles = []
    for icp in icp_profiles[:2]:
        icp_roles.extend(icp.get("job_titles", [])[:3])

    product = product_intelligence or {}
    product_context = ""
    if product.get("product_name") or product.get("main_problem_solved"):
        product_context = f"""
PRODUCT CONTEXT (use in outreach angles):
Product: {product.get("product_name", "")}
Solves: {product.get("main_problem_solved", "")}
Key Features: {product.get("main_features", [])[:3]}
"""

    prompt = f"""Generate 2-3 outreach-ready contact records for this company.

TARGET COMPANY: {target_company.name}
DOMAIN: {target_company.domain}
INDUSTRY: {target_company.industry}
SIZE: {target_company.company_size}
WHY THEY MATCH: {target_company.why_they_match}
PAIN POINTS THEY EXPERIENCE: {target_company.pain_points_matched}
{product_context}
RELEVANT ROLES FROM ICP: {icp_roles}
{scraped_summary}
{website_summary}

RULES:
- If scraped contacts are provided above, use THOSE names and titles exactly.
- For scraped contacts, set data_source to "scraped".
- If no scraped contacts exist, generate realistic names for the company/industry and set data_source to "inferred".
- For each contact:
  * full_name: exact name (from scraping) or realistic name (if inferred)
  * designation: exact title (from scraping) or realistic title matching an ICP role
  * department: department they belong to
  * seniority: one of "C-Suite", "VP", "Director", "Manager", "Senior IC"
  * linkedin_url: exact URL (from scraping) or empty string
  * email: if found on website use it; else derive from pattern firstname.lastname@{target_company.domain} only if confident; else empty
  * why_target: 1 sentence — why this specific person owns the pain point
  * outreach_angle: 1 SPECIFIC sentence referencing the product's solution to their SPECIFIC pain point at {target_company.name}
  * priority: "high", "medium", or "low"

Return TargetContactsForCompanyResponse JSON."""

    response = await call_groq_structured(
        system_prompt=_CONTACT_SYSTEM,
        user_prompt=prompt,
        output_schema=TargetContactsForCompanyResponse,
        model=_settings.groq_model_fast,
        max_tokens=2000,
    )
    return response.contacts


# ─── Target Company Discovery ─────────────────────────────────────────────────

_COMPANY_SYSTEM = """You are a B2B sales intelligence expert.
Given an ICP and product description, identify real prospect companies.
Output ONLY valid JSON matching TargetCompanyDiscoveryResponse."""


def _build_company_prompt(business_profile: dict, icp_profiles: list[dict]) -> str:
    company = business_profile.get("company_name", "")
    value_prop = business_profile.get("value_proposition", "")
    industry = business_profile.get("industry", "")
    geographies = business_profile.get("geographies", [])

    # Product intelligence for richer targeting
    product = business_profile.get("product_intelligence", {})
    product_context = ""
    if product.get("product_name") or product.get("main_features"):
        product_context = f"""
PRODUCT DETAILS:
Product: {product.get("product_name", company)}
Main Features: {product.get("main_features", [])}
Problem Solved: {product.get("main_problem_solved", "")}
Target Industry: {product.get("target_industry", industry)}
Ideal Company Size: {product.get("target_company_size", "")}
Use Cases: {product.get("use_cases", [])}
"""

    icp_summary = []
    for icp in icp_profiles[:2]:
        firm = icp.get("firmographics", {})
        icp_summary.append({
            "profile_name": icp.get("profile_name", ""),
            "industries": firm.get("industries", []),
            "company_sizes": firm.get("company_sizes", []),
            "geographies": firm.get("geographies", []) or geographies,
            "job_titles": icp.get("job_titles", []),
            "pain_points": [p.get("pain", "") for p in icp.get("pain_points", [])],
        })

    return f"""Identify 8 real companies that are ideal prospects for this product.

SELLER: {company}
VALUE PROPOSITION: {value_prop}
{product_context}
ICP PROFILES:
{json.dumps(icp_summary, indent=2)}

Select companies that:
1. Are in the target industry ({product.get("target_industry", industry) or industry})
2. Match the ideal company size ({product.get("target_company_size", "varies")})
3. Operate in the correct geographies: {geographies}
4. Would experience the main problem: {product.get("main_problem_solved", "")}

For each company:
- name: exact real company name (use real well-known companies, not fictional)
- domain: their website domain (e.g. "hdfc.com")
- linkedin_url: e.g. "https://linkedin.com/company/hdfc-bank"
- industry: their specific industry
- company_size: e.g. "500-5000 employees"
- headquarters: city, country
- why_they_match: 1-2 sentences referencing SPECIFIC product features they need
- icp_profile_name: which ICP profile they match
- pain_points_matched: 2-3 SPECIFIC pain points they experience that the product addresses
- priority: "high" (perfect fit), "medium" (good fit), or "low" (possible fit)

Return TargetCompanyDiscoveryResponse with "companies" array of 8 real companies."""


async def discover_target_companies(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
) -> list[TargetCompanySchema]:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError(f"Company {company_id} not found")

    business_profile = company.enriched_data.get("business_profile", {})
    icp_profiles = company.enriched_data.get("icp_profiles", [])

    if not icp_profiles:
        raise ValueError("ICP profiles required before target discovery")

    # Return cached
    existing = await db.execute(
        text("SELECT id FROM target_companies WHERE company_id = :cid LIMIT 1"),
        {"cid": str(company_id)},
    )
    if existing.first():
        rows = await db.execute(
            text("SELECT * FROM target_companies WHERE company_id = :cid ORDER BY priority, created_at"),
            {"cid": str(company_id)},
        )
        return [TargetCompanySchema(**dict(r)) for r in rows.mappings().all()]

    # Generate target companies via Groq
    prompt = _build_company_prompt(business_profile, icp_profiles)
    response = await call_groq_structured(
        system_prompt=_COMPANY_SYSTEM,
        user_prompt=prompt,
        output_schema=TargetCompanyDiscoveryResponse,
        model=_settings.groq_model_fast,
        max_tokens=3000,
    )

    # Collect ICP job titles for LinkedIn search
    icp_job_titles = []
    for icp in icp_profiles[:2]:
        icp_job_titles.extend(icp.get("job_titles", [])[:3])

    inserted = []
    for tc in response.companies:
        row = await db.execute(
            text("""
                INSERT INTO target_companies (
                    tenant_id, company_id, name, domain, linkedin_url, industry,
                    company_size, headquarters, why_they_match, icp_profile_name,
                    pain_points_matched, priority
                ) VALUES (
                    :tenant_id, :company_id, :name, :domain, :linkedin_url, :industry,
                    :company_size, :headquarters, :why_they_match, :icp_profile_name,
                    CAST(:pain_points_matched AS jsonb), :priority
                ) RETURNING id
            """),
            {
                "tenant_id": str(tenant_id), "company_id": str(company_id),
                "name": tc.name, "domain": tc.domain, "linkedin_url": tc.linkedin_url,
                "industry": tc.industry, "company_size": tc.company_size,
                "headquarters": tc.headquarters, "why_they_match": tc.why_they_match,
                "icp_profile_name": tc.icp_profile_name,
                "pain_points_matched": json.dumps(tc.pain_points_matched),
                "priority": tc.priority,
            },
        )
        tc_id = row.scalar()
        inserted.append((tc_id, tc))

    await db.commit()
    logger.info(f"Saved {len(inserted)} target companies for {company_id}")

    product_intelligence = business_profile.get("product_intelligence", {})

    # Discover contacts for all companies in parallel — each gets its own DB session
    async def _discover_one(tc_id: uuid.UUID, tc: TargetCompanySchema) -> None:
        async with AsyncSessionLocal() as session:
            try:
                await _discover_contacts_for_company(
                    company_id=company_id,
                    tenant_id=tenant_id,
                    target_company_id=tc_id,
                    target_company=tc,
                    icp_profiles=icp_profiles,
                    icp_job_titles=icp_job_titles,
                    product_intelligence=product_intelligence,
                    db=session,
                )
            except Exception as e:
                logger.error(f"Contact discovery failed for {tc.name}: {e}", exc_info=True)

    await asyncio.gather(*[_discover_one(tc_id, tc) for tc_id, tc in inserted])

    return response.companies


# ─── Contact Discovery per company ────────────────────────────────────────────

async def _discover_contacts_for_company(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    target_company_id: uuid.UUID,
    target_company: TargetCompanySchema,
    icp_profiles: list[dict],
    icp_job_titles: list[str],
    db: AsyncSession,
    product_intelligence: dict | None = None,
) -> None:
    logger.info(f"Discovering contacts for {target_company.name} via scraping...")

    # 1. Google Search for LinkedIn profile URLs + parse snippets
    google_contacts = await _google_search_linkedin_people(target_company.name, icp_job_titles)
    logger.info(f"  Google found {len(google_contacts)} profiles for {target_company.name}")

    # 2. Scrape LinkedIn profiles for real detail (name, title, company confirmed)
    scraped_profiles = []
    if google_contacts:
        linkedin_urls = [c["linkedin_url"] for c in google_contacts]
        scraped_profiles = await _scrape_linkedin_profiles(linkedin_urls)
        logger.info(f"  LinkedIn scraper returned {len(scraped_profiles)} profiles")

    # Merge: prefer scraped profile data, fall back to google snippet data
    merged_contacts = []
    for gc in google_contacts:
        # Find matching scraped profile by URL
        matched = next(
            (sp for sp in scraped_profiles if gc["linkedin_url"] in sp.get("linkedin_url", "")),
            None,
        )
        if matched and matched.get("full_name"):
            merged_contacts.append({
                "full_name": matched["full_name"],
                "designation": matched["current_title"] or gc["designation"],
                "linkedin_url": matched["linkedin_url"] or gc["linkedin_url"],
                "data_source": "linkedin_scraped",
            })
        else:
            # Use snippet data (google search result)
            if gc.get("full_name"):
                merged_contacts.append({**gc, "data_source": "google_snippet"})

    # 3. Scrape company website for team page + emails
    website_data = {}
    if target_company.domain:
        website_data = await _scrape_company_website(target_company.domain)

    # 4. Groq enriches with outreach angles + fills gaps
    contacts = await _groq_enrich_contacts(
        target_company=target_company,
        icp_profiles=icp_profiles,
        scraped_contacts=merged_contacts,
        website_data=website_data,
        product_intelligence=product_intelligence,
    )

    # Persist with data_source
    for c in contacts:
        # Resolve data_source: if name came from scraping, tag it
        scraping_match = next(
            (m for m in merged_contacts if m.get("full_name") == c.full_name),
            None,
        )
        data_source = scraping_match["data_source"] if scraping_match else "inferred"

        await db.execute(
            text("""
                INSERT INTO target_contacts (
                    tenant_id, company_id, target_company_id, company_name,
                    full_name, designation, department, seniority,
                    linkedin_url, email, why_target, outreach_angle,
                    priority, data_source
                ) VALUES (
                    :tenant_id, :company_id, :target_company_id, :company_name,
                    :full_name, :designation, :department, :seniority,
                    :linkedin_url, :email, :why_target, :outreach_angle,
                    :priority, :data_source
                )
            """),
            {
                "tenant_id": str(tenant_id),
                "company_id": str(company_id),
                "target_company_id": str(target_company_id),
                "company_name": target_company.name,
                "full_name": c.full_name,
                "designation": c.designation,
                "department": c.department,
                "seniority": c.seniority,
                "linkedin_url": c.linkedin_url,
                "email": c.email,
                "why_target": c.why_target,
                "outreach_angle": c.outreach_angle,
                "priority": c.priority,
                "data_source": data_source,
            },
        )

    await db.commit()
    logger.info(
        f"  Inserted {len(contacts)} contacts for {target_company.name} "
        f"({sum(1 for m in merged_contacts if m.get('data_source') != 'inferred')} from scraping)"
    )


# ─── Read helpers ─────────────────────────────────────────────────────────────

async def get_target_companies(company_id: uuid.UUID, db: AsyncSession) -> list[dict]:
    rows = await db.execute(
        text("SELECT * FROM target_companies WHERE company_id = :cid ORDER BY priority, created_at"),
        {"cid": str(company_id)},
    )
    return [dict(r) for r in rows.mappings().all()]


async def get_target_contacts(company_id: uuid.UUID, db: AsyncSession) -> list[dict]:
    rows = await db.execute(
        text("""
            SELECT tc.*, tco.name AS target_company_name, tco.domain AS target_company_domain
            FROM target_contacts tc
            LEFT JOIN target_companies tco ON tc.target_company_id = tco.id
            WHERE tc.company_id = :cid
            ORDER BY tc.priority, tco.name, tc.seniority
        """),
        {"cid": str(company_id)},
    )
    return [dict(r) for r in rows.mappings().all()]
