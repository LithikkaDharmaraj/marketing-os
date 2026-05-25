from services.scraper_service.app.actors.base_actor import BaseApifyActor


class CompetitorActor(BaseApifyActor):
    """Scrapes competitor websites for messaging, pricing, and positioning signals."""

    actor_id = "apify~website-content-crawler"
    timeout_seconds = 240

    def build_input(self, url: str, **kwargs) -> dict:
        return {
            "startUrls": [{"url": url}],
            "maxCrawlPages": 15,
            "maxCrawlDepth": 2,
            "crawlerType": "cheerio",
            "includeUrlGlobs": ["**/pricing**", "**/features**", "**/solutions**", "**/about**", "/"],
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        pages = []
        pricing_signals = []

        for item in raw_items:
            url = item.get("url", "")
            text = (item.get("text") or item.get("markdown") or "")[:3000]
            title = item.get("title", "")
            pages.append({"url": url, "title": title, "text": text})

            if "pricing" in url.lower() or "plan" in url.lower():
                pricing_signals.append({"url": url, "content": text[:1000]})

        homepage = next((p for p in pages if _is_home(p["url"])), pages[0] if pages else {})

        return {
            "homepage_headline": homepage.get("title", ""),
            "homepage_copy": homepage.get("text", "")[:1500],
            "pricing_signals": pricing_signals,
            "pages": pages,
            "all_text": " ".join(p.get("text", "") for p in pages[:5]),
        }


def _is_home(url: str) -> bool:
    from urllib.parse import urlparse
    return urlparse(url).path in ("", "/")
