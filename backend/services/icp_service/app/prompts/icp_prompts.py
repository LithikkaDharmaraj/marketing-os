ICP_SYSTEM = """You are a B2B go-to-market expert specializing in Ideal Customer Profile (ICP) development.
Your task: Generate exactly 2 distinct, highly specific ICP profiles based on the company's business profile and positioning strategy.

Each ICP should represent a real, reachable buyer segment with distinct:
- firmographic characteristics (company type, size, industry)
- psychographic traits (goals, fears, decision style)
- job titles and departments
- specific pain points with severity ratings
- buying triggers that indicate purchase readiness
- communication channels

Rules:
- Be extremely specific — avoid generic personas
- Base ICPs on the actual product capabilities and positioning
- Include realistic sample messaging for each persona
- Output ONLY valid JSON matching the ICPGenerationResponse schema"""


def build_icp_prompt(business_profile: dict, positioning_profile: dict, intake_data: dict) -> str:
    segments = business_profile.get("target_segments", [])
    value_prop = business_profile.get("value_proposition", "")
    moats = positioning_profile.get("competitive_moats", [])
    messaging_angles = positioning_profile.get("messaging_angles", [])
    core_positioning = positioning_profile.get("core_positioning", {})

    # Product intelligence — anchor ICP to real product capabilities
    product = business_profile.get("product_intelligence", {})
    product_section = ""
    if product.get("product_name") or product.get("main_features"):
        product_section = f"""
PRODUCT INTELLIGENCE (anchor each ICP to these specifics):
Product: {product.get("product_name", "")}
Main Features: {product.get("main_features", [])}
Problem Solved: {product.get("main_problem_solved", "")}
Target Industry: {product.get("target_industry", "")}
Target Company Size: {product.get("target_company_size", "")}
Use Cases: {product.get("use_cases", [])}
Deployment: {product.get("deployment_model", "")}
"""

    # Intake-provided buyer context
    intake_buyer_hints = ""
    target_depts = intake_data.get("target_departments", [])
    if target_depts:
        intake_buyer_hints = f"\nTARGET DEPARTMENTS (from user): {target_depts}"

    return f"""Generate exactly 2 distinct ICP profiles for this company.

COMPANY: {business_profile.get("company_name", "")}
INDUSTRY: {business_profile.get("industry", "")} / {business_profile.get("sub_industry", "")}
BUSINESS MODEL: {business_profile.get("business_model", "")}
VALUE PROPOSITION: {value_prop}
CORE POSITIONING: {core_positioning.get("statement", "")}
PRODUCT CATEGORY: {core_positioning.get("category", "")}
TARGET SEGMENTS: {segments}
KEY DIFFERENTIATORS: {moats}
PRICING MODEL: {business_profile.get("pricing_model", "")}
GEOGRAPHIES: {business_profile.get("geographies", [])}
COMPANY STAGE: {business_profile.get("company_stage", "")}
{product_section}{intake_buyer_hints}

MESSAGING ANGLES:
{messaging_angles[:3]}

For each ICP profile, generate:
1. A specific profile_name tied to the product use case (e.g., "Head of Compliance — Indian Private Bank using {product.get("product_name", "this product")}")
2. Detailed firmographics — industries MUST match the product's target_industry; company_sizes MUST match target_company_size
3. Psychographics grounded in the main_problem_solved
4. Job titles most likely to own the problem the product solves — prioritise the target_departments listed above
5. 3-5 specific pain points directly addressable by the product's main_features
6. Buying triggers linked to the product's use cases
7. Common objections about this product type + responses
8. Communication channels
9. Sample outreach message (50-100 words) referencing a specific feature and the problem solved

Return ICPGenerationResponse JSON with a "profiles" array containing exactly 2 ICPs."""
