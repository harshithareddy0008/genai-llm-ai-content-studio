"""Prompt assembly is a pure function; easy to test."""
from backend.prompts import PROMPTS
from backend.schemas import GenerateRequest
from backend.services.content_service import build_generation_prompt


def test_every_generation_task_has_system_prompt():
    assert set(PROMPTS) == {"email", "linkedin", "summary", "rewrite", "blog"}
    assert all(len(text) > 40 for text in PROMPTS.values())


def test_prompt_includes_requested_settings_and_boundaries():
    req = GenerateRequest(
        task="linkedin", input_text="Built a machine learning project",
        tone="confident", language="Telugu", length="long"
    )
    instruction, prompt = build_generation_prompt(req)
    assert "LinkedIn" in instruction
    assert "Tone: confident" in prompt
    assert "Target length: long" in prompt
    assert "Output language: Telugu" in prompt
    assert "--- BEGIN USER INPUT ---" in prompt
    assert "Built a machine learning project" in prompt
