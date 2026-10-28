"""Tests for SDK payloads using a fully mocked client."""
from types import SimpleNamespace

import pytest

from backend.schemas import ChatRequest, GenerateRequest, ChatMessage
from backend.services.llm_service import GeminiService, LLMProviderError, MissingAPIKeyError


class FakeModels:
    def __init__(self):
        self.kwargs = None
        self.error = None
        self.response_text = "Generated successfully"

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def settings(key="test", model="test-model"):
    return SimpleNamespace(gemini_api_key=key, gemini_model=model)


def test_key_is_required_for_real_sdk_client():
    with pytest.raises(MissingAPIKeyError):
        GeminiService(settings(key=""))


def test_generate_sends_system_prompt_and_generation_config():
    client = FakeClient()
    service = GeminiService(settings(), client=client)
    result = service.generate(GenerateRequest(task="blog", input_text="How NLP works", length="long"))
    assert result == "Generated successfully"
    assert client.models.kwargs["model"] == "test-model"
    config = client.models.kwargs["config"]
    assert "blog writer" in config.system_instruction
    assert config.max_output_tokens == 4096
    assert "How NLP works" in client.models.kwargs["contents"]


def test_chat_passes_history_with_correct_gemini_roles():
    client = FakeClient()
    service = GeminiService(settings(), client=client)
    result = service.chat(ChatRequest(message="What next?", history=[
        ChatMessage(role="user", content="I wrote a Python app"),
        ChatMessage(role="assistant", content="Well done"),
    ]))
    assert result == "Generated successfully"
    contents = client.models.kwargs["contents"]
    assert [item.role for item in contents] == ["user", "model", "user"]


def test_empty_provider_answer_gets_safe_error():
    client = FakeClient()
    client.models.response_text = "  "
    service = GeminiService(settings(), client=client)
    with pytest.raises(LLMProviderError, match="no text"):
        service.generate(GenerateRequest(task="email", input_text="Write an email"))


def test_quota_error_is_mapped_to_429():
    client = FakeClient()
    exc = RuntimeError("Secret request data")
    exc.code = 429
    client.models.error = exc
    service = GeminiService(settings(), client=client)
    with pytest.raises(LLMProviderError) as info:
        service.generate(GenerateRequest(task="email", input_text="Write an email"))
    assert info.value.status_code == 429
    assert "Secret request data" not in str(info.value)
