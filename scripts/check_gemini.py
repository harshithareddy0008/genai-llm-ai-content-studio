"""Optional LIVE smoke test. This makes one real API call and may use quota."""
from backend.config import get_settings
from backend.schemas import GenerateRequest
from backend.services.llm_service import GeminiService, MissingAPIKeyError, LLMProviderError


def main():
    try:
        service = GeminiService(get_settings())
        output = service.generate(GenerateRequest(
            task="email",
            input_text="Write a short friendly email thanking my Python mentor.",
            length="short", tone="friendly",
        ))
    except (MissingAPIKeyError, LLMProviderError) as exc:
        print(f"Could not complete smoke test: {exc}")
        raise SystemExit(1) from exc
    print(f"SUCCESS - model: {service.model}\n")
    print(output)


if __name__ == "__main__":
    main()
