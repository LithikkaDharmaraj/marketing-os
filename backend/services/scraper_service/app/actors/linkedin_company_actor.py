from services.scraper_service.app.actors.base_actor import BaseApifyActor


class LinkedInCompanyActor(BaseApifyActor):
    actor_id = "harvestapi~linkedin-company"
    timeout_seconds = 180

    def build_input(self, linkedin_url: str, **kwargs) -> dict:
        return {
            "companies": [linkedin_url],
            "proxy": {"useApifyProxy": True},
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        if not raw_items:
            return {}
        item = raw_items[0]
        return {
            "company_name": item.get("name", "") or item.get("companyName", ""),
            "tagline": item.get("tagline", ""),
            "description": item.get("description", ""),
            "employee_count": item.get("staffCount", 0) or item.get("employeeCount", 0),
            "employee_count_range": item.get("staffCountRange", "") or item.get("employeeCountRange", ""),
            "founded_year": item.get("foundedOn", {}).get("year") if isinstance(item.get("foundedOn"), dict) else item.get("foundedYear"),
            "headquarters": item.get("headquartersLine1", "") or item.get("headquarters", ""),
            "industries": item.get("industries", []),
            "specialities": item.get("specialities", []) or item.get("specialties", []),
            "website": item.get("website", "") or item.get("websiteUrl", ""),
            "linkedin_followers": item.get("followersCount", 0),
            "company_type": item.get("companyType", "") or item.get("type", ""),
        }


class LinkedInProfileActor(BaseApifyActor):
    actor_id = "pratikdani~linkedin-people-profile-scraper"
    timeout_seconds = 180

    def build_input(self, profile_urls: list[str], **kwargs) -> dict:
        return {
            "profileUrls": profile_urls,
            "proxy": {"useApifyProxy": True},
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        profiles = []
        for item in raw_items:
            profiles.append({
                "full_name": f"{item.get('firstName', '')} {item.get('lastName', '')}".strip(),
                "headline": item.get("headline", ""),
                "current_title": item.get("positions", [{}])[0].get("title", "") if item.get("positions") else "",
                "current_company": item.get("positions", [{}])[0].get("companyName", "") if item.get("positions") else "",
                "location": item.get("location", ""),
                "summary": item.get("summary", ""),
                "linkedin_url": item.get("linkedinUrl", ""),
                "connections": item.get("connectionsCount", 0),
            })
        return {"profiles": profiles}
