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

    return f"""Generate exactly 2 distinct ICP profiles for this company.

COMPANY: {business_profile.get("company_name", "")}
INDUSTRY: {business_profile.get("industry", "")} / {business_profile.get("sub_industry", "")}
BUSINESS MODEL: {business_profile.get("business_model", "")}
VALUE PROPOSITION: {value_prop}
CORE POSITIONING: {core_positioning.get("statement", "")}
PRODUCT CATEGORY: {core_positioning.get("category", "")}
TARGET SEGMENTS (from intake): {segments}
KEY DIFFERENTIATORS: {moats}
PRICING MODEL: {business_profile.get("pricing_model", "")}
GEOGRAPHIES: {business_profile.get("geographies", [])}
COMPANY STAGE: {business_profile.get("company_stage", "")}

MESSAGING ANGLES AVAILABLE:
{messaging_angles[:3]}

GOALS FROM INTAKE:
{intake_data.get("goals", [])}

For each ICP profile, generate:
1. A specific profile_name (e.g., "Enterprise Compliance Head — Indian Private Bank")
2. Detailed firmographics (industries, company_sizes, revenue_ranges, geographies, funding_stages, tech_stack_signals)
3. Psychographics (goals, fears, values, decision_style, success_metrics)
4. Job titles, seniority levels, departments
5. 3-5 specific pain points (with severity: high/medium/low and current_solution)
6. 3-5 buying triggers
7. Common objections
8. Communication channels
9. Sample outreach message (50-100 words, use the company's positioning)

Return ICPGenerationResponse JSON with a "profiles" array containing exactly 2 ICPs."""
