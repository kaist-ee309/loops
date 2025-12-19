"""
API routes aggregator - imports router and OpenAPI tags from routes module.
"""

from app.api.routes import OPENAPI_TAGS, router

__all__ = ["router", "OPENAPI_TAGS"]
