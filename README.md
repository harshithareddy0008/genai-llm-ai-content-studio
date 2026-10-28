# ✨ AI Content Studio — GenAI + Gemini LLM Project

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B)](https://streamlit.io/)
[![LLM](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4)](https://ai.google.dev/gemini-api/docs)

A complete **first Generative AI + LLM portfolio project** built with **Google Gemini**, **FastAPI**, **Streamlit**, **Python** and **uv**. It deliberately avoids RAG and AI agents: those are separate projects in the learning roadmap.

## 1. What does it do?

| Feature | What the user can do |
|---|---|
| 📧 Email Generator | Draft polished emails from simple instructions |
| 💼 LinkedIn Post Generator | Turn project/achievement notes into posts |
| 📋 Text Summarizer | Summarize pasted text without inventing facts |
| ✏️ Text Rewriter | Improve grammar and tone |
| 📰 Blog Generator | Draft structured educational articles |
| 💬 AI Chat Assistant | Chat with session-scoped conversation context |

Additional options: tone, answer length, language and temperature; text download; API validation; error handling; optional shared API token; mocked offline tests.

## 2. Architecture

```text
User in browser
      ↓
Streamlit frontend (frontend/app.py)
      ↓ POST /generate or /chat, JSON over HTTP
FastAPI backend (backend/main.py)
      ↓ Pydantic validation
Task-specific prompt (backend/prompts/)
      ↓
Gemini service (backend/services/llm_service.py)
      ↓
Google Gemini Developer API
      ↓
Generated text returned to Streamlit
```

Detailed explanation: [`docs/architecture.md`](docs/architecture.md).

## 3. Folder structure

```text
genai-llm-ai-content-studio/
├── backend/
│   ├── main.py                  # FastAPI routes
│   ├── config.py                # API key and model configuration
│   ├── dependencies.py          # Gemini dependency and optional app token
│   ├── schemas.py               # Pydantic request/response models
│   ├── prompts/                 # Reusable task instructions
│   └── services/
│       ├── content_service.py   # Prompt assembly
│       └── llm_service.py       # Google Gemini API integration
├── frontend/
│   ├── app.py                   # Streamlit website
│   └── ui_helpers.py            # Backend API requests
├── tests/                        # Offline pytest tests
├── scripts/check_gemini.py       # Optional live API smoke test
├── docs/architecture.md
├── .streamlit/config.toml
├── .env.example
├── .python-version
├── .gitignore
├── pyproject.toml
├── uv.lock                     # Created when you run uv sync
├── Dockerfile.api
├── Dockerfile.frontend
├── compose.yaml
├── render.yaml
└── README.md
```

## 4. Setup: VS Code + uv

**Requirements:** Python 3.11, [uv](https://docs.astral.sh/uv/getting-started/installation/), Git, a Gemini Developer API key. Python 3.10 is also supported by the project, but 3.11 is the tested default target.

**Step 1.** Unzip, open the folder in VS Code, then open its terminal:

```bash
cd genai-llm-ai-content-studio
uv sync
```

`uv sync` resolves dependencies from `pyproject.toml`, sets up `.venv` and **creates `uv.lock`**. Commit that generated lockfile to GitHub so future installs are reproducible.

**Step 2.** Get your API key at [Google AI Studio](https://aistudio.google.com/api-keys).

**Step 3.** Create the actual `.env` file:

macOS / Linux / Git Bash:
```bash
cp .env.example .env
```
Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```dotenv
GEMINI_API_KEY=your_real_gemini_key
GEMINI_MODEL=gemini-3.5-flash-lite
APP_ACCESS_TOKEN=some_long_random_shared_secret
API_BASE_URL=http://127.0.0.1:8000
```

**Security:** Never commit `.env`, your API key, or any real secrets. The `.gitignore` excludes it. The default is **`gemini-3.5-flash-lite`**, a current stable, cost-conscious choice with an eligible free tier (subject to quotas). Older models such as `gemini-2.5-flash` may have restricted access for new projects. Gemini model availability, account pricing and quotas can change: verify your model in AI Studio, and update `GEMINI_MODEL` if necessary.

## 5. Start the project locally

Open **two terminals** inside the project root.

**Terminal 1 — FastAPI:**

```bash
uv run uvicorn backend.main:app --reload
```

Check:
- Health: <http://127.0.0.1:8000/health>
- API Swagger documentation: <http://127.0.0.1:8000/docs>

**Terminal 2 — Streamlit:**

```bash
uv run streamlit run frontend/app.py
```

Visit <http://localhost:8501>.

## 6. Test Gemini API (one live call)

After adding your real key:

```bash
uv run python -m scripts.check_gemini
```

This **makes an actual API request** and uses provider quota. It is *not* part of pytest.

## 7. Automated tests (no API key needed)

```bash
uv run pytest -q
uv run ruff check backend frontend tests scripts
```

Tests use fakes instead of calling Google. They validate all five generation tasks, chat, request validation, optional access-token protection, prompt templates, and Gemini SDK argument construction.

## 8. API examples

A generation request to `POST http://127.0.0.1:8000/generate`:

```json
{
  "task": "email",
  "input_text": "Write an internship request email for a Python developer role",
  "tone": "professional",
  "length": "medium",
  "language": "English",
  "temperature": 0.6
}
```

Set HTTP header `X-App-Token: some_long_random_shared_secret` if `APP_ACCESS_TOKEN` is configured.

Example successful response (illustrative, not a guaranteed model output):

```json
{
  "task": "email",
  "generated_text": "Subject: Inquiry About Python Internship Opportunities\n\nDear Hiring Team, ...",
  "model": "gemini-3.5-flash-lite"
}
```

`POST /chat` expects:

```json
{
  "message": "How can I improve my Python resume?",
  "history": [
    {"role": "user", "content": "I am applying for software roles."},
    {"role": "assistant", "content": "Good luck with your applications!"}
  ],
  "temperature": 0.6
}
```

Chat history is limited to 12 previous messages in each request. It lives in Streamlit session state and disappears when the browser session ends or is reset.

## 9. Run using Docker Compose

Install Docker Desktop / Docker Engine, then:

```bash
docker compose up --build
```

The `.env` file must exist for Docker Compose. The first build resolves dependencies and writes a lockfile inside the image; run `uv sync` locally and commit its resulting `uv.lock` for future reproducibility. Open http://localhost:8501. Backend docs: http://localhost:8000/docs.

## 10. Deploy to Render (two services)

1. Push the project to a **new GitHub repository** named `genai-llm-ai-content-studio`. Do **not** push `.env`.
2. Go to [Render](https://dashboard.render.com/) → **New → Blueprint** and connect the repository (or create two separate Python web services from the same repo).
3. `render.yaml` defines both `ai-content-studio-api` (FastAPI) and `ai-content-studio-web` (Streamlit). Actual URL names depend on account and service naming.
4. In backend environment variables, set `GEMINI_API_KEY` to the real key, `GEMINI_MODEL` to an available model, and `APP_ACCESS_TOKEN` to a strong secret.
5. In frontend environment variables, set `API_BASE_URL` to your **actual** backend URL, e.g. `https://your-real-api-name.onrender.com` (no placeholder should remain) and set `APP_ACCESS_TOKEN` to exactly the same secret as backend.
6. Deploy both services. Test `/health` on the API, then open the frontend and generate content.

Render Blueprint service config (already included):

| Service | Build command | Start command |
|---|---|---|
| FastAPI | `pip install uv && uv sync --no-dev` | `uv run --no-sync uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Streamlit | `pip install uv && uv sync --no-dev` | `uv run --no-sync streamlit run frontend/app.py --server.address 0.0.0.0 --server.port $PORT` |

**Note:** Render free instances can sleep and may be slow to wake. See the latest [Render documentation](https://render.com/docs/web-services) for current plan limits.

## 11. Troubleshooting

| Symptom | Solution |
|---|---|
| `503` Gemini API key missing | Edit `.env` or Render backend secret `GEMINI_API_KEY` |
| `401` from FastAPI | Both services must have matching `APP_ACCESS_TOKEN` |
| `429` rate limit | Wait, reduce usage, inspect Gemini quota |
| `502` model unavailable | Check `GEMINI_MODEL` in AI Studio; select a supported model |
| Streamlit says backend unreachable | Verify FastAPI started and `API_BASE_URL` correct |
| `uv` not found | Install uv: https://docs.astral.sh/uv/getting-started/installation/ |
| `.env` uploaded to GitHub | **Rotate the API key immediately** and remove it from repository history |

## 12. Interview explanation

> I built AI Content Studio, a full-stack Generative AI application using the Google Gemini LLM. A Streamlit interface provides five writing tools plus a chatbot. A FastAPI backend validates requests using Pydantic, selects task-specific prompt templates, and calls the Gemini API using the official Google Gen AI Python SDK. I added tone, output length, temperature controls, basic multi-turn chat, mocked automated tests, Docker containers and Render deployment configuration. I intentionally kept this first project focused on direct LLM generation; RAG and agents are separate portfolio projects.

## 13. Important limitations

- An LLM is not guaranteed to be accurate. Review output before publishing.
- Text prompts go to a third-party model provider for processing; **do not upload sensitive data**.
- Gemini API keys, quotas and bills are managed in your Google account.
- The optional access token is just a shared backend secret, **not** end-user identity/authentication. Public access may require user auth, rate limits, abuse prevention and quotas.
- This is direct LLM prompting: **not RAG, not an autonomous tool-calling agent, not multi-agent AI**.

## Official references

- [Gemini API docs](https://ai.google.dev/gemini-api/docs)
- [Google Gen AI SDK](https://googleapis.github.io/python-genai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://docs.streamlit.io/)
- [uv](https://docs.astral.sh/uv/)
- [Render Blueprint reference](https://render.com/docs/blueprint-spec)
