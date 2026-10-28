"""One isolated Gemini adapter: the rest of the project does not know SDK details."""
from typing import Any

from google import genai
from google.genai import types

from backend.config import Settings
from backend.prompts import CHAT_PROMPT
from backend.schemas import ChatRequest, GenerateRequest
from backend.services.content_service import build_generation_prompt


class MissingAPIKeyError(RuntimeError):
    """Raised when the server has no Gemini API key configured."""


class LLMProviderError(RuntimeError):
    """Provider-related errors without exposing the underlying secrets/details."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class GeminiService:
    def __init__(self, settings: Settings, client: Any = None):
        self.model = settings.gemini_model
        if client is None:
            if not settings.gemini_api_key.strip() or settings.gemini_api_key.startswith(
                "replace_with_"
            ):
                raise MissingAPIKeyError(
                    "GEMINI_API_KEY is missing. Set a valid key in .env or Render."
                )
            self.client = genai.Client(api_key=settings.gemini_api_key)
        else:
            # Test injection: never calls the real external API.
            self.client = client

    @staticmethod
    def _raise_provider_error(exc: Exception) -> None:
        # Do not echo exception details: third-party exceptions can include requests.
        code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        try:
            code = int(code)
        except (TypeError, ValueError):
            code = None
        if code == 429:
            raise LLMProviderError(
                "Gemini rate limit reached. Please retry later or review your API quota.",
                status_code=429,
            ) from exc
        if code in (401, 403):
            raise LLMProviderError(
                "Gemini authentication failed. Check the server's API key and permissions.",
                status_code=502,
            ) from exc
        if code == 404:
            raise LLMProviderError(
                "Gemini model unavailable. Verify GEMINI_MODEL in Google AI Studio.",
                status_code=502,
            ) from exc
        raise LLMProviderError(
            "Gemini could not generate a response. Check service status and try again."
        ) from exc

    def _call(self, *, contents: Any, instruction: str, temperature: float, max_tokens: int) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=instruction,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            result = response.text if response else None
            if not result or not result.strip():
                raise LLMProviderError(
                    "Gemini returned no text. Try a different prompt or model settings."
                )
            return result.strip()
        except LLMProviderError:
            raise
        except Exception as exc:
            self._raise_provider_error(exc)
            raise AssertionError("unreachable")  # pragma: no cover

    def generate(self, request: GenerateRequest) -> str:
        instruction, user_prompt = build_generation_prompt(request)
        # Long articles need more output tokens than short emails.
        tokens = {"short": 1024, "medium": 2048, "long": 4096}[request.length]
        return self._call(
            contents=user_prompt,
            instruction=instruction,
            temperature=request.temperature,
            max_tokens=tokens,
        )

    def chat(self, request: ChatRequest) -> str:
        history: list[types.Content] = []
        for message in request.history:
            role = "model" if message.role == "assistant" else "user"
            history.append(
                types.Content(role=role, parts=[types.Part.from_text(text=message.content)])
            )
        history.append(
            types.Content(role="user", parts=[types.Part.from_text(text=request.message)])
        )
        return self._call(
            contents=history,
            instruction=CHAT_PROMPT,
            temperature=request.temperature,
            max_tokens=2048,
        )
