#!/usr/bin/env python3
"""Seed development data — creates a default tenant and sample company."""
import asyncio, sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from shared.config import get_settings

settings = get_settings()

TENANT_ID = "00000000-0000-0000-0000-000000000001"
COMPANY_ID = "00000000-0000-0000-0000-000000000002"


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Seed tenant
        await session.execute(
            text("""
                INSERT INTO tenants (id, slug, name, plan)
                VALUES (:id, 'dev-tenant', 'Dev Tenant', 'enterprise')
                ON CONFLICT (id) DO NOTHING
            """),
            {"id": TENANT_ID},
        )

        # Seed sample company
        await session.execute(
            text("""
                INSERT INTO companies (id, tenant_id, name, domain, website_url, industry, business_model, company_size, intake_data)
                VALUES (:id, :tid, 'Lendkraft', 'lendkraft.ai', 'https://lendkraft.ai', 'FinTech', 'B2B SaaS', '50-200', '{}')
                ON CONFLICT (id) DO NOTHING
            """),
            {"id": COMPANY_ID, "tid": TENANT_ID},
        )

        await session.commit()
        print(f"Seeded: tenant={TENANT_ID}, company={COMPANY_ID}")


if __name__ == "__main__":
    asyncio.run(seed())
