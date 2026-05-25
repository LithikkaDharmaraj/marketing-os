from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.config import get_settings
from shared.utils.logging import configure_logging
from services.intelligence_service.app.router import router
import shared.models.tenant  # noqa: F401
import shared.models.company  # noqa: F401

configure_logging("intelligence-service")
settings = get_settings()

app = FastAPI(title="Intelligence Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "intelligence-service"}
