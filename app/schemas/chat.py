from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.chat import MessageRole
from app.models.user import LanguageLevel


def _without_blanks(value: str, field: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} cannot be empty.")
    return cleaned


def _strip_optional(value: str | None, field: str) -> str | None:
    if value is None:
        return None
    return _without_blanks(value, field)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        return _without_blanks(value, "Message content")


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    feedback: str | None = None
    model_name: str | None = None
    tokens_used: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessagePage(BaseModel):
    items: list[MessageOut]
    total: int
    limit: int
    offset: int


class AIChatResponse(BaseModel):
    """Structured output returned by the AI language tutor service."""

    reply: str = Field(..., min_length=1)
    feedback: str | None = None
    suggested_title: str | None = Field(default=None, max_length=100)


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", min_length=1, max_length=100)
    target_language: str | None = Field(default=None, min_length=1, max_length=50)
    level: LanguageLevel | None = None
    topic: str | None = Field(default=None, min_length=1, max_length=150)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return _without_blanks(value, "Title")

    @field_validator("target_language")
    @classmethod
    def strip_target_language(cls, value: str | None) -> str | None:
        return _strip_optional(value, "Target language")

    @field_validator("topic")
    @classmethod
    def strip_topic(cls, value: str | None) -> str | None:
        return _strip_optional(value, "Topic")


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    target_language: str | None = Field(default=None, min_length=1, max_length=50)
    level: LanguageLevel | None = None
    topic: str | None = Field(default=None, min_length=1, max_length=150)
    is_archived: bool | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        return _strip_optional(value, "Title")

    @field_validator("target_language")
    @classmethod
    def strip_target_language(cls, value: str | None) -> str | None:
        return _strip_optional(value, "Target language")

    @field_validator("topic")
    @classmethod
    def strip_topic(cls, value: str | None) -> str | None:
        return _strip_optional(value, "Topic")


class ConversationOut(BaseModel):
    id: int
    user_id: int
    title: str
    target_language: str | None = None
    level: LanguageLevel | None = None
    topic: str | None = None
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationPage(BaseModel):
    items: list[ConversationOut]
    total: int
    limit: int
    offset: int


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]
