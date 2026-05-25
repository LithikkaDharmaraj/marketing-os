import hashlib


def compute_hash(company_id: str, source_url: str, content: str) -> str:
    """SHA-256 of company+url+content for dedup key."""
    raw = f"{company_id}::{source_url}::{content[:1000]}"
    return hashlib.sha256(raw.encode()).hexdigest()


def is_duplicate(existing_hashes: set[str], new_hash: str) -> bool:
    return new_hash in existing_hashes
