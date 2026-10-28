"""Client-side HTTP calls and labels, independent of the Streamlit UI."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

FEATURES = {
    "Email Generator": ("email", "Explain the email you need", "Write an email requesting a Python internship at a software company."),
    "LinkedIn Post": ("linkedin", "Topic or project details", "I built a Streamlit ML fraud detection app and learned imbalanced classification."),
    "Text Summarizer": ("summary", "Paste the text to summarize", "Paste an article, notes, or a paragraph here..."),
    "Text Rewriter": ("rewrite", "Paste the text to improve", "I am writing to ask for the opportunity to interview with your company."),
    "Blog Generator": ("blog", "Describe the topic and key points", "Explain how machine learning can help detect digital-payment fraud."),
}

TONES = ["professional", "friendly", "formal", "casual", "confident"]
LENGTHS = ["short", "medium", "long"]


class FrontendAPIError(RuntimeError):
    """Friendly frontend exception for all upstream failures."""


def api_request(endpoint: str, payload: dict) -> dict:
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    token = os.getenv("APP_ACCESS_TOKEN", "")
    headers = {"X-App-Token": token} if token else {}
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            json=payload,
            headers=headers,
            timeout=(5, 120),
        )
    except requests.Timeout as exc:
        raise FrontendAPIError("Request timed out. Try again in a moment.") from exc
    except requests.RequestException as exc:
        raise FrontendAPIError("Cannot reach the FastAPI server. Check its URL and deployment.") from exc
    if not response.ok:
        try:
            detail = response.json().get("detail", "Unknown API error")
            if isinstance(detail, (dict, list)):
                detail = "Please check the input and try again."
        except ValueError:
            detail = "The backend returned an invalid response."
        raise FrontendAPIError(f"API error ({response.status_code}): {detail}")
    try:
        return response.json()
    except ValueError as exc:
        raise FrontendAPIError("The backend returned invalid JSON.") from exc
