BUSINESS_INTELLIGENCE_SYSTEM = """You are a senior B2B marketing analyst specializing in business intelligence extraction.
Analyze all provided company data and extract structured intelligence.

Your task: Extract comprehensive business intelligence from scraped company data.
Focus on: industry classification, business model, value proposition, target segments, competitive landscape, and growth signals.

Output ONLY valid JSON. Be specific and data-driven. Avoid vague language."""


def build_intelligence_prompt(intake_data: dict, scraped_data: dict) -> str:
    website_text = scraped_data.get("website", {}).get("all_text", "")[:3000]
    linkedin_data = scraped_data.get("linkedin", {})
    crunchbase_data = scraped_data.get("crunchbase", {})

    return f"""Analyze this company and extract structured business intelligence.

INTAKE FORM DATA:
Company: {intake_data.get("company_name", "")}
Website: {intake_data.get("website_url", "")}
Industry (self-reported): {intake_data.get("industry", "")}
Business Model: {intake_data.get("business_model", "")}
Product Type: {intake_data.get("product_type", "")}
Geography: {intake_data.get("geography", "")}
Company Size: {intake_data.get("company_size", "")}
Target Market: {intake_data.get("target_market", "")}
Services/Products: {intake_data.get("services_products", "")}
Goals: {intake_data.get("goals", [])}

WEBSITE CONTENT (first 3000 chars):
{website_text}

LINKEDIN DATA:
Employee Count: {linkedin_data.get("employee_count", "unknown")}
Specialities: {linkedin_data.get("specialities", [])}
Tagline: {linkedin_data.get("tagline", "")}
Description: {linkedin_data.get("description", "")}

CRUNCHBASE DATA:
Funding Stage: {crunchbase_data.get("funding_stage", "unknown")}
Total Funding: ${crunchbase_data.get("total_funding_usd", 0):,}
Categories: {crunchbase_data.get("categories", [])}

COMPETITORS PROVIDED: {intake_data.get("competitors", [])}

Extract the complete BusinessProfileSchema JSON for this company."""


# ── Competitor Discovery ────────────────────────────────────────────────────

COMPETITOR_DISCOVERY_SYSTEM = """You are a senior B2B competitive intelligence analyst with deep knowledge of the global SaaS and technology market.

Your task: Discover real competitors for a company based on its profile and market context.

Rules:
1. Use your training knowledge of real companies in this market to identify genuine competitors.
2. DO NOT include companies from the "User-Provided Hints" list — those are handled separately.
3. Discover 4-6 direct competitors (same category, similar audience and pricing).
4. Discover 2-3 indirect or emerging competitors (adjacent category or alternative solution).
5. For each competitor, provide accurate, specific intelligence — not generic descriptions.
6. Base competitiveness on: target audience overlap, feature similarity, pricing tier, messaging similarity, brand strength.

Competitiveness level — output EXACTLY ONE of these strings:
- "Highly Competitive"     — strong overlap across audience, features, pricing, and messaging
- "Moderately Competitive" — some overlap but meaningful differences exist
- "Less Competitive"       — different segment, audience, or pricing tier

Discovery sources — set discovery_source to one of:
- "ai_reasoning"      — discovered using your market knowledge
- "google_search"     — inferred from search result data provided

Output ONLY valid JSON matching the CompetitorDiscoveryResponse schema. No explanation, no markdown."""


def build_competitor_discovery_prompt(
    business_profile: dict,
    scraped_data: dict,
    user_provided_hints: list[str],
) -> str:
    website = scraped_data.get("website", {})
    headline = website.get("homepage_headline", "")
    copy = (website.get("homepage_copy", "") or "")[:1000]
    all_text = (website.get("all_text", "") or "")[:1500]

    google = scraped_data.get("google_search", {})
    search_results = google.get("results", [])
    search_snippets = "\n".join(
        f"- {r.get('title','')}: {r.get('description','')[:150]}"
        for r in search_results[:6]
        if r.get("title")
    )

    company_name = business_profile.get("company_name", "")
    industry = business_profile.get("industry", "")
    sub_industry = business_profile.get("sub_industry", "")
    value_prop = business_profile.get("value_proposition", "")
    segments = business_profile.get("target_segments", [])
    differentiators = business_profile.get("key_differentiators", [])
    pricing_model = business_profile.get("pricing_model", "")
    geographies = business_profile.get("geographies", [])
    business_model = business_profile.get("business_model", "")
    market_position = business_profile.get("market_position", "")
    categories = business_profile.get("core_product_categories", [])

    hints_str = "\n".join(f"- {h}" for h in user_provided_hints) if user_provided_hints else "None"

    return f"""Discover competitors for this company.

COMPANY PROFILE:
Name: {company_name}
Industry: {industry} / {sub_industry}
Business Model: {business_model}
Value Proposition: {value_prop}
Product Categories: {categories}
Target Segments: {segments}
Key Differentiators: {differentiators}
Pricing Model: {pricing_model}
Geographies: {geographies}
Market Position: {market_position}

WEBSITE INTELLIGENCE:
Headline: {headline}
Homepage Copy: {copy}
Content Excerpt: {all_text}

GOOGLE SEARCH RESULTS (for market context):
{search_snippets or "Not available"}

USER-PROVIDED HINTS (context only — DO NOT include these in your output):
{hints_str}

Discover 4-6 direct competitors and 2-3 indirect/emerging competitors.
Exclude any company already listed in the User-Provided Hints above.
Return CompetitorDiscoveryResponse JSON."""


# ── User-Suggested Competitor Enrichment ───────────────────────────────────

COMPETITOR_EXTRACTION_SYSTEM = """You are a competitive intelligence analyst for a B2B marketing strategy team.

Analyze competitor website content and extract structured competitive intelligence.

For competitiveness_level, output EXACTLY ONE of these strings (no other values are valid):
- "Highly Competitive"    — strong brand; significant overlap in positioning, audience, features, and/or pricing
- "Moderately Competitive" — some overlap but meaningful differences exist in positioning or target audience
- "Less Competitive"     — minimal overlap; different market segment, audience, or pricing tier

Base the classification on inferred signals: market positioning overlap, feature similarity,
audience overlap, brand strength, pricing tier overlap, messaging similarity.

Output ONLY valid JSON matching the DiscoveredCompetitor schema. No explanation, no markdown."""


def build_competitor_prompt(
    company_name: str,
    competitor_url: str,
    competitor_data: dict,
    company_context: str = "",
) -> str:
    homepage_headline = competitor_data.get("homepage_headline", "")
    homepage_copy = (competitor_data.get("homepage_copy", "") or "")[:1200]
    pricing_signals = competitor_data.get("pricing_signals", [])[:3]
    all_text = (competitor_data.get("all_text", "") or "")[:1500]

    return f"""Analyze this competitor and extract full competitive intelligence for {company_name}.

COMPETITOR:
URL: {competitor_url}
Homepage Headline: {homepage_headline}
Homepage Copy: {homepage_copy}
Pricing Signals: {pricing_signals}
Content Excerpt: {all_text}

OUR COMPANY (for differentiation context):
Name: {company_name}
{company_context}

Extract a DiscoveredCompetitor JSON. Set:
- user_provided: true
- discovered_by_ai: false
- discovery_source: "user_provided"
- competitor_type: direct (unless clearly indirect)
- differentiation_opportunities: specific ways {company_name} can outperform this competitor
- weaknesses: their weaknesses relative to {company_name}
Infer competitiveness_level based on how directly this competitor overlaps with {company_name}."""
