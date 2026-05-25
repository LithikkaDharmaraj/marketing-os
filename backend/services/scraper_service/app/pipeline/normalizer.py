"""Maps each source's structured_data to a common enriched company schema."""


def normalize(source_type: str, structured_data: dict) -> dict:
    fn = _SOURCE_MAP.get(source_type)
    if fn:
        return fn(structured_data)
    return structured_data


def _normalize_website(data: dict) -> dict:
    return {
        "description": data.get("homepage", {}).get("text_preview", "")[:1000],
        "emails": data.get("emails", []),
        "phones": data.get("phones", []),
        "ctas": data.get("ctas", []),
        "pages_crawled": data.get("total_pages_crawled", 0),
        "pricing_content": data.get("pricing_page", {}).get("text_preview", ""),
        "all_text": data.get("all_text", "")[:5000],
    }


def _normalize_linkedin(data: dict) -> dict:
    return {
        "employee_count": data.get("employee_count", 0),
        "employee_range": data.get("employee_count_range", ""),
        "founded_year": data.get("founded_year"),
        "headquarters": data.get("headquarters", ""),
        "industries": data.get("industries", []),
        "specialities": data.get("specialities", []),
        "followers": data.get("linkedin_followers", 0),
        "tagline": data.get("tagline", ""),
        "description": data.get("description", ""),
    }


def _normalize_crunchbase(data: dict) -> dict:
    return {
        "funding_stage": data.get("last_funding_type", ""),
        "total_funding_usd": data.get("total_funding_usd", 0),
        "founded_on": data.get("founded_on", ""),
        "categories": data.get("categories", []),
        "investors": data.get("investors", []),
        "employee_count": data.get("employee_count", ""),
    }


def _normalize_competitor(data: dict) -> dict:
    return {
        "headline": data.get("homepage_headline", ""),
        "homepage_copy": data.get("homepage_copy", ""),
        "pricing_signals": data.get("pricing_signals", []),
        "all_text": data.get("all_text", "")[:3000],
    }


def _normalize_google(data: dict) -> dict:
    return {
        "search_results": data.get("search_results", []),
        "knowledge_panel": data.get("knowledge_panel", {}),
    }


def _normalize_reddit(data: dict) -> dict:
    return {
        "pain_points": [p.get("title", "") for p in data.get("pain_point_posts", [])],
        "subreddits": data.get("top_subreddits", []),
    }


def _normalize_reviews(data: dict) -> dict:
    return {
        "pros_themes": data.get("pros_themes", []),
        "cons_themes": data.get("cons_themes", []),
        "reviews": data.get("reviews", [])[:5],
    }


def _normalize_builtwith(data: dict) -> dict:
    return {
        "tech_stack": data.get("tech_stack", {}),
        "categories": data.get("top_categories", []),
    }


_SOURCE_MAP = {
    "website": _normalize_website,
    "linkedin": _normalize_linkedin,
    "crunchbase": _normalize_crunchbase,
    "competitor": _normalize_competitor,
    "google_search": _normalize_google,
    "reddit": _normalize_reddit,
    "reviews": _normalize_reviews,
    "builtwith": _normalize_builtwith,
}
