"""Cleans raw scraped content: truncation, boilerplate removal, PII noise stripping."""
import re

_BOILERPLATE_PATTERNS = [
    r"cookie\s+policy",
    r"privacy\s+policy",
    r"terms\s+of\s+(service|use)",
    r"all\s+rights\s+reserved",
    r"©\s*\d{4}",
    r"subscribe\s+to\s+our\s+newsletter",
    r"sign\s+up\s+for\s+updates",
]
_BOILERPLATE_RE = re.compile("|".join(_BOILERPLATE_PATTERNS), re.IGNORECASE)

_PHONE_RE = re.compile(r"\+?[\d\s\-().]{10,20}")
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

MAX_PAGE_BYTES = 50_000  # 50KB cap per page
MAX_ALL_TEXT_CHARS = 10_000


def clean_text(text: str, max_chars: int = MAX_ALL_TEXT_CHARS) -> str:
    """Strip boilerplate lines and truncate."""
    if not text:
        return ""
    lines = text.splitlines()
    cleaned = [l for l in lines if not _BOILERPLATE_RE.search(l)]
    result = "\n".join(cleaned)
    return result[:max_chars]


def strip_pii(text: str) -> str:
    """Remove emails and phone numbers from free text."""
    text = _EMAIL_RE.sub("[email]", text)
    text = _PHONE_RE.sub("[phone]", text)
    return text


def clean_structured(data: dict, source_type: str) -> dict:
    """Apply source-specific cleaning to normalized data."""
    if source_type == "website":
        if "all_text" in data:
            data["all_text"] = clean_text(data["all_text"])
        if "description" in data:
            data["description"] = clean_text(data["description"], max_chars=500)
    elif source_type == "competitor":
        if "all_text" in data:
            data["all_text"] = clean_text(data["all_text"], max_chars=3000)
        if "homepage_copy" in data:
            data["homepage_copy"] = clean_text(data["homepage_copy"], max_chars=1000)
    elif source_type in ("reddit", "reviews"):
        for key in ("pain_points", "pros_themes", "cons_themes"):
            if key in data and isinstance(data[key], list):
                data[key] = [clean_text(str(item), max_chars=300) for item in data[key][:10]]
    return data
