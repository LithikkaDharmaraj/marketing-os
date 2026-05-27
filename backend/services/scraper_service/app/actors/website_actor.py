from services.scraper_service.app.actors.base_actor import BaseApifyActor


class WebsiteActor(BaseApifyActor):
    """Crawls company website and extracts structured content."""

    actor_id = "apify~website-content-crawler"
    timeout_seconds = 300

    def build_input(self, url: str, **kwargs) -> dict:
        return {
            "startUrls": [{"url": url}],
            "maxCrawlPages": 30,
            "maxCrawlDepth": 3,
            "crawlerType": "cheerio",
            "excludeUrlGlobs": ["**/*.pdf", "**/*.zip", "**/cdn-cgi/**"],
            "saveFiles": False,
            "saveScreenshots": False,
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        pages = []
        emails, phones, ctas = set(), set(), []

        for item in raw_items:
            url = item.get("url", "")
            text = item.get("text", "") or item.get("markdown", "")
            title = item.get("title", "")
            metadata = item.get("metadata", {}) or {}

            pages.append({
                "url": url,
                "title": title,
                "text_preview": text[:2000] if text else "",
                "meta_description": metadata.get("description", ""),
                "meta_keywords": metadata.get("keywords", ""),
                "is_homepage": _is_homepage(url),
                "is_pricing": _is_pricing_page(url),
                "is_product": _is_product_page(url),
                "is_contact": _is_contact_page(url),
            })

            if text:
                for e in _extract_emails(text):
                    emails.add(e)
                for p in _extract_phones(text):
                    phones.add(p)
                ctas.extend(_extract_ctas(text, url))

        homepage = next((p for p in pages if p["is_homepage"]), pages[0] if pages else {})
        pricing_page = next((p for p in pages if p["is_pricing"]), {})
        product_page = next((p for p in pages if p.get("is_product")), {})

        homepage_text = homepage.get("text_preview", "")
        return {
            "pages": pages,
            "homepage": homepage,
            "pricing_page": pricing_page,
            "product_page": product_page,
            "emails": list(emails)[:10],
            "phones": list(phones)[:5],
            "ctas": list(set(ctas))[:20],
            "total_pages_crawled": len(pages),
            "all_text": " ".join(p.get("text_preview", "") for p in pages[:10]),
            # Convenience top-level fields used by LLM prompts
            "homepage_headline": homepage.get("title", ""),
            "homepage_copy": homepage_text[:1500],
            "product_page_text": product_page.get("text_preview", "")[:2000],
            "pricing_page_text": pricing_page.get("text_preview", "")[:1000],
            "pricing_signals": _extract_pricing_signals(pricing_page.get("text_preview", "")),
        }


def _is_homepage(url: str) -> bool:
    from urllib.parse import urlparse
    p = urlparse(url)
    return p.path in ("", "/", "/index", "/home")


def _is_pricing_page(url: str) -> bool:
    return any(kw in url.lower() for kw in ["pricing", "plans", "price"])


def _is_contact_page(url: str) -> bool:
    return any(kw in url.lower() for kw in ["contact", "reach", "support"])


def _is_product_page(url: str) -> bool:
    return any(kw in url.lower() for kw in ["product", "features", "solution", "platform", "how-it-works", "capabilities"])


def _extract_pricing_signals(text: str) -> list[str]:
    import re
    signals = []
    price_matches = re.findall(r"\$[\d,]+(?:/(?:mo|month|yr|year|user))?", text, re.IGNORECASE)
    signals.extend(price_matches[:5])
    tier_matches = re.findall(r"(starter|basic|pro|professional|enterprise|growth|business|free|premium|team)\s+plan", text, re.IGNORECASE)
    signals.extend(list(dict.fromkeys(m.strip() for m in tier_matches))[:4])
    return signals[:8]


def _extract_emails(text: str) -> list[str]:
    import re
    return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)


def _extract_phones(text: str) -> list[str]:
    import re
    return re.findall(r"[\+]?[1-9][0-9 .\-\(\)]{8,}[0-9]", text)


def _extract_ctas(text: str, url: str) -> list[str]:
    import re
    cta_patterns = [
        r"(Get Started|Book a Demo|Request Demo|Free Trial|Sign Up|Contact Us|Schedule a Call)[^\n]{0,30}",
    ]
    results = []
    for pattern in cta_patterns:
        results.extend(re.findall(pattern, text, re.IGNORECASE))
    return results[:5]
