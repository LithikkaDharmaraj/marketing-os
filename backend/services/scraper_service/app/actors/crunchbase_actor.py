from services.scraper_service.app.actors.base_actor import BaseApifyActor


class CrunchbaseActor(BaseApifyActor):
    actor_id = "epctex~crunchbase-scraper"
    timeout_seconds = 180

    def build_input(self, domain: str, **kwargs) -> dict:
        return {
            "startUrls": [{"url": f"https://www.crunchbase.com/organization/{domain.split('.')[0]}"}],
            "proxy": {"useApifyProxy": True},
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        if not raw_items:
            return {}
        item = raw_items[0]
        return {
            "company_name": item.get("name", ""),
            "short_description": item.get("short_description", ""),
            "founded_on": item.get("founded_on", ""),
            "employee_count": item.get("num_employees_enum", ""),
            "total_funding_usd": item.get("total_funding_usd", 0),
            "last_funding_type": item.get("last_funding_type", ""),
            "last_funding_at": item.get("last_funding_at", ""),
            "ipo_status": item.get("ipo_status", ""),
            "headquarters": item.get("location_identifiers", []),
            "categories": item.get("category_groups", []),
            "investors": item.get("investors", [])[:5],
            "website": item.get("website_url", ""),
            "linkedin": item.get("linkedin", {}).get("value", ""),
            "twitter": item.get("twitter", {}).get("value", ""),
        }
