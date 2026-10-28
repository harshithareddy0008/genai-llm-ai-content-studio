"""Request/response contracts shared by the API's endpoints."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Task = Literal["email", "linkedin", "summary", "rewrite", "blog"]
Tone = Literal["professional", "friendly", "formal", "casual", "confident"]
Length = Literal["short", "medium", "long"]


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: Task
    input_text: str = Field(min_length=3, max_length=12000)
    tone: Tone = "professional"
    length: Length = "medium"
    language: str = Field(default="English", min_length=2, max_length=40)
    temperature: float = Field(default=0.6, ge=0.0, le=1.0)

    @field_validator("input_text", "language")
    @classmethod
    def no_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("The field must not be blank")
        return value.strip()


class GenerateResponse(BaseModel):
    task: Task
    generated_text: str
    model: str


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Chat messages cannot be blank")
        return value.strip()


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)
    temperature: float = Field(default=0.6, ge=0.0, le=1.0)

    @field_validator("message")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message cannot be blank")
        return value.strip()


class ChatResponse(BaseModel):
    reply: str
    model: str
