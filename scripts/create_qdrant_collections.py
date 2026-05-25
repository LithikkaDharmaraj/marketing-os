#!/usr/bin/env python3
"""Initialize Qdrant collections for Marketing OS."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.embedding_service.app.service import ensure_collections


async def main():
    print("Creating Qdrant collections...")
    await ensure_collections()
    print("Done. Collections created: icp_profiles, positioning_profiles, campaign_context")


if __name__ == "__main__":
    asyncio.run(main())
