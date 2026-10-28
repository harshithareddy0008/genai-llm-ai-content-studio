# System architecture and request lifecycle

```text
   Visitor (browser)
          |
          v
  Streamlit frontend    -- HTTPS JSON -->  FastAPI backend
  frontend/app.py                       backend/main.py
          |                                   |
          |                           Pydantic validates fields
          |                                   |
          |                           prompt selected by task
          |                                   |
          |                           GeminiService via SDK
          |                                   |
          |                               Gemini API
          |                                   |
          +<------------ JSON response -------+
```

## The five content-generation tasks

Each task reuses the same `/generate` route but gets its own system prompt:

- `email`: subject, greeting, body, closing
- `linkedin`: authentic professional post
- `summary`: grounded summarization of pasted text
- `rewrite`: grammar, clarity and tone
- `blog`: article with headings

`/chat` is the sixth feature. The browser stores the conversation in Streamlit
`session_state`. The frontend sends up to twelve previous turns to FastAPI; FastAPI
maps `assistant` to Gemini's `model` role and sends each turn in order.

## Why these modules?

- `schemas.py` rejects malformed inputs before making expensive LLM calls.
- `prompts/` isolates writing instructions from provider API code.
- `content_service.py` assembles task context and safe boundaries for source text.
- `llm_service.py` is the only module importing the Google Gen AI SDK.
- `dependencies.py` adds optional app-token checking; tests inject fake LLM service.
- `frontend/ui_helpers.py` controls HTTP requests and displays friendly errors.

## Key security and deployment notes

- Gemini key exists **only** on backend; never put it in Streamlit UI code.
- Set identical `APP_ACCESS_TOKEN` on Streamlit and FastAPI for public deployments.
- Shared token is a minimal safeguard, **not** true individual user authentication,
  bot prevention, or a production billing/quota strategy.
- Without APP_ACCESS_TOKEN the API is unauthenticated: use only in trusted local dev.
- Content sent to Google is processed under your provider account's terms.
- Streamlit session state is temporary; there is no persistent database.
- No retrieval, vector database, tool calling, autonomous agents, or agent orchestration.
- For public use consider rate limiting, request size caps, user auth and cost controls.
