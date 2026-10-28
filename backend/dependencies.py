"""FastAPI dependencies; override these in unit tests."""
from functools import lru_cache
import secrets

from fastapi import Header, HTTPException

from backend.config import get_settings
from backend.services.llm_service import GeminiService


@lru_cache
def get_gemini_service() -> GeminiService:
    return GeminiService(get_settings())


def verify_app_token(x_app_token: str | None = Header(default=None)) -> None:
    """Optional shared secret to stop anonymous callers of public API endpoints.

    If APP_ACCESS_TOKEN is empty the endpoint is public (local development only).
    """
    expected = get_settings().app_access_token
    if expected and not secrets.compare_digest(x_app_token or "", expected):
        raise HTTPException(status_code=401, detail="Missing or invalid app access token")
