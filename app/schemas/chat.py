from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.chat import MessageRole


def _without_blanks(value: str, field: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} cannot be empty.")
    return cleaned


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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessagePage(BaseModel):
    items: list[MessageOut]
    total: int
    limit: int
    offset: int


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return _without_blanks(value, "Title")


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _without_blanks(value, "Title")


class ConversationOut(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]
