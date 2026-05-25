from services.scraper_service.app.actors.base_actor import BaseApifyActor


class RedditSignalsActor(BaseApifyActor):
    """Scrapes Reddit for pain point discussions related to the company's market."""

    actor_id = "trudax~reddit-scraper"
    timeout_seconds = 180

    def build_input(self, industry: str, pain_keywords: list[str] = None, **kwargs) -> dict:
        keywords = pain_keywords or [industry]
        return {
            "searches": [f"{kw} problems OR pain OR frustrated OR hate OR slow" for kw in keywords[:3]],
            "maxItems": 50,
            "proxy": {"useApifyProxy": True},
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        posts = []
        for item in raw_items:
            posts.append({
                "title": item.get("title", ""),
                "text": (item.get("text") or "")[:500],
                "subreddit": item.get("community", ""),
                "score": item.get("score", 0),
                "num_comments": item.get("numberOfComments", 0),
                "url": item.get("url", ""),
                "sentiment": "negative" if _is_pain_post(item.get("title", "")) else "neutral",
            })

        # Sort by engagement
        posts.sort(key=lambda x: x["score"] + x["num_comments"] * 2, reverse=True)

        return {
            "pain_point_posts": [p for p in posts if p["sentiment"] == "negative"][:10],
            "all_posts": posts[:20],
            "top_subreddits": list({p["subreddit"] for p in posts if p["subreddit"]})[:5],
        }


def _is_pain_post(title: str) -> bool:
    pain_words = ["problem", "issue", "pain", "frustrated", "hate", "slow", "broken", "fail", "struggle", "difficult"]
    return any(w in title.lower() for w in pain_words)


class ReviewSitesActor(BaseApifyActor):
    """Scrapes G2/Capterra for review sentiment signals."""

    actor_id = "apify~web-scraper"
    timeout_seconds = 180

    def build_input(self, product_name: str, **kwargs) -> dict:
        return {
            "startUrls": [
                {"url": f"https://www.g2.com/search?query={product_name.replace(' ', '+')}"},
            ],
            "pageFunction": """async function pageFunction(context) {
                const { page } = context;
                const reviews = await page.$$eval('.review-card', cards =>
                    cards.slice(0, 20).map(card => ({
                        rating: card.querySelector('.stars')?.getAttribute('data-rating') || '',
                        title: card.querySelector('.review-title')?.textContent?.trim() || '',
                        pros: card.querySelector('.pros')?.textContent?.trim() || '',
                        cons: card.querySelector('.cons')?.textContent?.trim() || '',
                    }))
                );
                return reviews;
            }""",
            "maxRequestsPerCrawl": 5,
        }

    def normalize(self, raw_items: list[dict]) -> dict:
        reviews = []
        for item in raw_items:
            if isinstance(item, list):
                reviews.extend(item)
            elif isinstance(item, dict):
                reviews.append(item)

        return {
            "reviews": reviews[:20],
            "pros_themes": _extract_themes([r.get("pros", "") for r in reviews]),
            "cons_themes": _extract_themes([r.get("cons", "") for r in reviews]),
        }


def _extract_themes(texts: list[str]) -> list[str]:
    all_text = " ".join(texts).lower()
    themes = []
    theme_keywords = {
        "ease of use": ["easy", "simple", "intuitive", "user-friendly"],
        "performance": ["fast", "slow", "performance", "speed"],
        "support": ["support", "customer service", "help"],
        "pricing": ["expensive", "affordable", "price", "cost"],
        "features": ["feature", "functionality", "missing"],
    }
    for theme, keywords in theme_keywords.items():
        if any(kw in all_text for kw in keywords):
            themes.append(theme)
    return themes


class BuiltWithActor(BaseApifyActor):
    """Fetches tech stack data from BuiltWith."""

    actor_id = "ecomdate~builtwith-domain-scraper"
    timeout_seconds = 120

    def build_input(self, domain: str, **kwargs) -> dict:
        return {"domains": [domain]}

    def normalize(self, raw_items: list[dict]) -> dict:
        if not raw_items:
            return {}
        item = raw_items[0]
        # ecomdate actor returns technologies in different structure
        technologies = item.get("technologies", []) or item.get("techStack", [])
        categories: dict[str, list[str]] = {}
        for tech in technologies:
            if isinstance(tech, dict):
                cat = tech.get("category", "") or tech.get("categories", ["Other"])[0] if tech.get("categories") else "Other"
                name = tech.get("name", "") or tech.get("technology", "")
            else:
                cat, name = "Other", str(tech)
            if name:
                categories.setdefault(cat, []).append(name)

        return {
            "tech_stack": categories,
            "total_technologies": len(technologies),
            "top_categories": list(categories.keys())[:10],
        }
