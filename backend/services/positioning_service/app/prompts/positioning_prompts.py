POSITIONING_SYSTEM = """You are a world-class B2B positioning strategist, trained on frameworks from April Dunford (Obviously Awesome),
Geoffrey Moore (Crossing the Chasm), and the best SaaS go-to-market playbooks.

Your task: Generate a complete positioning strategy for a B2B company based on their business profile and competitive landscape.

Rules:
- Be specific and opinionated — avoid generic statements
- Ground every claim in the provided data
- Create messaging angles that address real emotional triggers
- Generate segment-specific positioning for each target buyer
- Output ONLY valid JSON"""


def build_positioning_prompt(business_profile: dict, scraped_data: dict, intake_data: dict) -> str:
    competitor_data = []
    for key, data in scraped_data.items():
        if key.startswith("competitor"):
            competitor_data.append(f"URL: {data.get('homepage_headline', '')} — Copy: {data.get('homepage_copy', '')[:500]}")

    reddit_pain_points = scraped_data.get("reddit", {}).get("pain_points", [])
    review_cons = scraped_data.get("reviews", {}).get("cons_themes", [])

    # Product intelligence — the core driver
    product = business_profile.get("product_intelligence", {})
    product_section = ""
    if product.get("product_name") or product.get("main_features"):
        product_section = f"""
PRODUCT INTELLIGENCE (use this to anchor all positioning):
Product: {product.get("product_name", "")}
Description: {product.get("product_description", "")}
Main Features: {product.get("main_features", [])}
Problem Solved: {product.get("main_problem_solved", "")}
Target Industry: {product.get("target_industry", "")}
Target Company Size: {product.get("target_company_size", "")}
Deployment: {product.get("deployment_model", "")}
Use Cases: {product.get("use_cases", [])}
Pricing Signals: {product.get("pricing_signals", [])}
"""

    return f"""Generate a comprehensive positioning strategy for this company.

BUSINESS PROFILE:
Company: {business_profile.get("company_name", "")}
Industry: {business_profile.get("industry", "")} / {business_profile.get("sub_industry", "")}
Business Model: {business_profile.get("business_model", "")}
Value Proposition: {business_profile.get("value_proposition", "")}
Core Products: {business_profile.get("core_product_categories", [])}
Target Segments: {business_profile.get("target_segments", [])}
Key Differentiators: {business_profile.get("key_differentiators", [])}
Market Position: {business_profile.get("market_position", "")}
Company Stage: {business_profile.get("company_stage", "")}
{product_section}
COMPETITIVE LANDSCAPE:
{chr(10).join(competitor_data) if competitor_data else "No competitor data available"}

Existing Competitors (named):
{business_profile.get("competitive_landscape", [])}

MARKET PAIN SIGNALS (Reddit/Reviews):
Reddit pain points: {reddit_pain_points[:5]}
Customer cons from reviews: {review_cons}

GOALS FROM INTAKE:
{intake_data.get("goals", [])}

Generate the complete PositioningProfileSchema JSON. Ground every claim in the product intelligence above.
Include:
- core_positioning (statement, category, market_frame, unique_mechanism — reference specific product features)
- segment_positioning (for each target segment — headline, tagline, proof_point)
- messaging_angles (at least 4 angles — Speed, ROI, Risk, Trust — tied to specific features/use cases)
- emotional_triggers (fear, aspiration, FOMO — reference the main problem solved)
- competitive_moats (genuine differentiators based on features vs named competitors)
- objection_handling (top 3 objections + responses referencing product proof points)
- brand_personality (3-5 traits)"""
