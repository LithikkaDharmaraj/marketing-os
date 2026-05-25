from services.scraper_service.app.actors.base_actor import BaseApifyActor


class GoogleSearchActor(BaseApifyActor):
    actor_id = "apify~google-search-scraper"
    timeout_seconds = 120

    def build_input(self, company_name: str, domain: str, **kwargs) -> dict:
        # apify~google-search-scraper requires queries as a newline-separated string
        queries = "\n".join([
            f'"{company_name}" reviews',
            f'"{company_name}" vs competitors',
            f'site:{domain}',
        ])
        return {
            "queries": queries,
            "maxPagesPerQuery": 1,
            "resultsPerPage": 10,
            "languageCode": "en",
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        results = []
        for item in raw_items:
            for result in item.get("organicResults", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "position": result.get("position", 0),
                })
        return {
            "search_results": results[:20],
            "knowledge_panel": raw_items[0].get("knowledgeGraph", {}) if raw_items else {},
        }
