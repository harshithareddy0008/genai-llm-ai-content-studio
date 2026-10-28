# START HERE — AI Content Studio (Project 1)

## Beginner-friendly 5-step setup

1. **Unzip** the project and open `genai-llm-ai-content-studio` in VS Code.
2. Open the VS Code terminal inside that project, then run `uv sync`. This downloads required packages and creates `uv.lock`.
3. Create an API key in [Google AI Studio](https://aistudio.google.com/api-keys). Make a `.env` file by copying `.env.example`, and replace the placeholder with your actual key. Set the same `APP_ACCESS_TOKEN` for frontend and backend (they share one `.env` locally).
4. Open two terminal windows:
   - Terminal 1: `uv run uvicorn backend.main:app --reload`
   - Terminal 2: `uv run streamlit run frontend/app.py`
5. Visit **http://localhost:8501** to try all six features.

## Test the code

Run `uv run pytest -q` (offline unit tests — no Gemini usage).

Optional real Gemini API check: `uv run python -m scripts.check_gemini`.

## Deploy later

Follow the Render section in `README.md`; you will deploy two separate web services from one GitHub repository and configure the real frontend-to-backend URL.

**Important:** This starter bundle was generated without a `uv.lock` because package-registry access was unavailable in its build environment. The first `uv sync` creates it automatically. Live Gemini API requests and Render deployment require your own key and account.
