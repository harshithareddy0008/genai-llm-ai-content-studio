"""Task-specific instruction templates for the Gemini model."""

from backend.prompts.blog_prompt import system_prompt as blog_system
from backend.prompts.email_prompt import system_prompt as email_system
from backend.prompts.linkedin_prompt import system_prompt as linkedin_system
from backend.prompts.rewrite_prompt import system_prompt as rewrite_system
from backend.prompts.summary_prompt import system_prompt as summary_system

PROMPTS = {
    "email": email_system,
    "linkedin": linkedin_system,
    "summary": summary_system,
    "rewrite": rewrite_system,
    "blog": blog_system,
}

CHAT_PROMPT = (
    "You are a helpful, clear, friendly writing and learning assistant. "
    "Respond accurately, distinguish facts from guesses, and say when you do not know. "
    "Never claim to have browsed, executed code, or accessed files. "
    "Prefer useful, reasonably concise answers in the user's language."
)
