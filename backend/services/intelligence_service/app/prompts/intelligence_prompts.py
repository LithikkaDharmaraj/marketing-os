BUSINESS_INTELLIGENCE_SYSTEM = """You are a senior B2B marketing analyst specializing in business intelligence extraction.
Analyze all provided company data and extract structured intelligence.

PRIMARY FOCUS:
1. Product intelligence — what the product does, who it's for, what problem it solves
2. Target customer profile — industry, company size, departments, use cases
3. Value proposition and key differentiators
4. Growth signals and market position

The product_intelligence block is critical — it drives all downstream ICP generation,
target company discovery, and outreach context.

competitive_landscape: list 2-3 known competitors by name only (lightweight).
Do NOT elaborate on competitors — that is not the primary purpose of this platform.

Be specific and data-driven. Avoid vague language.
Output ONLY valid JSON."""


def build_intelligence_prompt(intake_data: dict, scraped_data: dict) -> str:
    website = scraped_data.get("website", {})
    homepage_headline = website.get("homepage_headline", "") or (website.get("homepage", {}) or {}).get("title", "")
    homepage_copy = (website.get("homepage_copy", "") or "")[:1200]
    product_page_text = (website.get("product_page_text", "") or "")[:2000]
    pricing_page_text = (website.get("pricing_page_text", "") or "")[:800]
    pricing_signals = website.get("pricing_signals", [])

    linkedin_data = scraped_data.get("linkedin", {})
    crunchbase_data = scraped_data.get("crunchbase", {})

    # User-provided product hints — seeds for AI to enrich
    intake_product_hints = ""
    product_description = intake_data.get("product_description", "")
    main_problem_solved = intake_data.get("main_problem_solved", "")
    target_industry = intake_data.get("target_industry", [])
    target_company_size = intake_data.get("target_company_size", "")
    target_departments = intake_data.get("target_departments", [])
    if any([product_description, main_problem_solved, target_industry, target_company_size, target_departments]):
        intake_product_hints = f"""
PRODUCT HINTS (user-provided — enrich from website):
Description: {product_description}
Main Problem Solved: {main_problem_solved}
Target Industry: {target_industry}
Target Company Size: {target_company_size}
Main Buyer Departments: {target_departments}
"""

    return f"""Analyze this company and extract comprehensive business + product intelligence.

INTAKE:
Company: {intake_data.get("company_name", "")}
Website: {intake_data.get("website_url", "")}
Industry (self-reported): {intake_data.get("industry", "")}
Geography: {intake_data.get("geography", "")}
Pricing Range: {intake_data.get("pricing_range", "")}
{intake_product_hints}
WEBSITE HOMEPAGE:
Headline: {homepage_headline}
Copy: {homepage_copy}

PRODUCT / FEATURES PAGE:
{product_page_text if product_page_text else "(not found — infer from homepage)"}

PRICING PAGE:
{pricing_page_text if pricing_page_text else "(not found — infer from content)"}
Pricing signals: {pricing_signals}

LINKEDIN:
Employees: {linkedin_data.get("employee_count", "unknown")}
Tagline: {linkedin_data.get("tagline", "")}
Specialities: {linkedin_data.get("specialities", [])}
Description: {(linkedin_data.get("description", "") or "")[:400]}

CRUNCHBASE:
Funding Stage: {crunchbase_data.get("funding_stage", "unknown")}
Total Funding: ${crunchbase_data.get("total_funding_usd", 0):,}
Categories: {crunchbase_data.get("categories", [])}

COMPETITORS PROVIDED: {intake_data.get("competitors", [])}

Extract the complete BusinessProfileSchema JSON including a fully populated product_intelligence block.
The product_intelligence block MUST contain:
- product_name: exact product/service name from website
- product_description: 2-3 sentences describing what it does
- main_features: 5-7 specific features (from product/features page or homepage)
- main_problem_solved: the single biggest problem it solves
- target_industry: the primary industry vertical it serves
- target_company_size: ideal customer company size (e.g. "100-5000 employees", "Enterprise 500+")
- deployment_model: Cloud SaaS / On-premise / Hybrid / API
- use_cases: 3-5 specific use cases
- pricing_signals: pricing tiers or price points found"""


