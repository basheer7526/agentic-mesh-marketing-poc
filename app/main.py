"""
Marketing News Intelligence Agent — FastAPI application entrypoint.

Start with:
    uvicorn app.main:app --reload

Swagger UI:    http://127.0.0.1:8000/docs
OpenAPI JSON:  http://127.0.0.1:8000/openapi.json
"""

import sys

from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import settings

# Reconfigure stdout/stderr to UTF-8 so that LLM-generated Unicode
# characters (em-dashes, non-breaking hyphens, arrows, etc.) in
# agent print() calls never crash on Windows cp1252 consoles.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered marketing news intelligence pipeline. "
        "Collects, deduplicates, scores, analyses, and "
        "prioritises marketing articles into an executive digest."
    ),
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(
    router,
    prefix="/api/v1",
)
