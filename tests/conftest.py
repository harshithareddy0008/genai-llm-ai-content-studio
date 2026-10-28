"""All endpoint tests are offline: Gemini is replaced by this stub."""
import pytest
from fastapi.testclient import TestClient

from backend.config import get_settings
from backend.dependencies import get_gemini_service
from backend.main import app


class FakeLLM:
    model = "fake-gemini-test-model"

    def generate(self, request):
        return f"Mock {request.task} output for {request.input_text}"

    def chat(self, request):
        return f"Mock chat reply: {request.message}"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("APP_ACCESS_TOKEN", "test-shared-token")
    get_settings.cache_clear()
    app.dependency_overrides[get_gemini_service] = lambda: FakeLLM()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers():
    return {"X-App-Token": "test-shared-token"}
