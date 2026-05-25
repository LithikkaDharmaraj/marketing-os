"""Qdrant collection definitions for Marketing OS vector memory."""

COLLECTIONS = {
    "icp_profiles": {
        "size": 384,
        "distance": "Cosine",
        "description": "ICP profile embeddings for similarity search",
    },
    "positioning_profiles": {
        "size": 384,
        "distance": "Cosine",
        "description": "Positioning profile embeddings for competitor analysis",
    },
    "campaign_context": {
        "size": 384,
        "distance": "Cosine",
        "description": "Reusable campaign memory for content generation",
    },
    "competitors": {
        "size": 384,
        "distance": "Cosine",
        "description": "Competitor profile embeddings for market similarity search",
    },
}
