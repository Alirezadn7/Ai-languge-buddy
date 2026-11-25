import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.models.chat import Conversation, Message, MessageRole
from app.models.user import LanguageLevel, User, UserProfile
from app.schemas.chat import (
    AIChatResponse,
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    ConversationPage,
    ConversationUpdate,
    MessageCreate,
    MessageOut,
)


@pytest.mark.asyncio
async def test_user_and_profile_creation(db):
    user = User(
        email="learner@example.com",
        hashed_password="hashed_secret",
        profile=UserProfile(
            native_language="fa",
            target_language="en",
            level=LanguageLevel.B1,
        ),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user, attribute_names=["profile"])

    assert user.id is not None
    assert user.profile.id is not None
    assert user.profile.native_language == "fa"
    assert user.profile.target_language == "en"
    assert user.profile.level == LanguageLevel.B1
    assert user.profile.user_id == user.id


@pytest.mark.asyncio
async def test_conversation_and_messages_cascade(db):
    user = User(
        email="chat_user@example.com",
        hashed_password="hashed_secret",
        profile=UserProfile(),
    )
    db.add(user)
    await db.flush()

    conv = Conversation(user_id=user.id, title="English Practice")
    db.add(conv)
    await db.flush()

    msg1 = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Hello, how are you?",
    )
    msg2 = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="I am doing well, thank you!",
        feedback="Good greeting!",
    )
    db.add_all([msg1, msg2])
    await db.commit()

    # Query conversation with messages
    stmt = select(Conversation).where(Conversation.id == conv.id)
    res = await db.scalar(stmt)
    await db.refresh(res, attribute_names=["messages"])

    assert len(res.messages) == 2
    assert res.messages[0].role == MessageRole.USER
    assert res.messages[1].role == MessageRole.ASSISTANT
    assert res.messages[1].feedback == "Good greeting!"

    # Test cascade delete: deleting conversation should delete messages
    await db.delete(conv)
    await db.commit()

    messages_in_db = (
        await db.scalars(select(Message).where(Message.conversation_id == conv.id))
    ).all()
    assert len(messages_in_db) == 0


@pytest.mark.asyncio
async def test_chat_model_extended_fields_and_schemas(db):
    user = User(
        email="extended_chat@example.com",
        hashed_password="hashed_secret",
        profile=UserProfile(),
    )
    db.add(user)
    await db.flush()

    conv = Conversation(
        user_id=user.id,
        title="Cafe Roleplay",
        target_language="de",
        level=LanguageLevel.B2,
        topic="Ordering Coffee",
    )
    db.add(conv)
    await db.flush()

    sys_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.SYSTEM,
        content="You are a friendly German barista.",
    )
    user_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="Ich mochte ein Kaffee, bitte.",
    )
    ai_msg = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="Gerne! Welchen Kaffee mochten Sie?",
        feedback="Use 'möchte einen Kaffee' (masculine accusative).",
        model_name="gemini-2.5-flash",
        tokens_used=42,
    )
    db.add_all([sys_msg, user_msg, ai_msg])
    await db.commit()
    await db.refresh(conv, attribute_names=["messages"])

    assert conv.is_archived is False
    assert conv.created_at is not None
    assert conv.updated_at is not None
    assert [m.role for m in conv.messages] == [
        MessageRole.SYSTEM,
        MessageRole.USER,
        MessageRole.ASSISTANT,
    ]
    assert conv.messages[2].model_name == "gemini-2.5-flash"
    assert conv.messages[2].tokens_used == 42
    assert "Conversation" in repr(conv)
    assert "Message" in repr(conv.messages[0])

    # Verify Pydantic schemas serialize ORM instances cleanly
    conv_out = ConversationOut.model_validate(conv)
    assert conv_out.target_language == "de"
    assert conv_out.level == LanguageLevel.B2
    assert conv_out.topic == "Ordering Coffee"

    conv_detail = ConversationDetail.model_validate(conv)
    assert len(conv_detail.messages) == 3
    assert MessageOut.model_validate(ai_msg).tokens_used == 42

    page = ConversationPage(items=[conv_out], total=1, limit=20, offset=0)
    assert page.total == 1
    assert len(page.items) == 1


def test_chat_schemas_validation():
    conv_in = ConversationCreate(
        title="  Daily Practice  ",
        target_language="  en  ",
        level=LanguageLevel.B1,
        topic="  Travel  ",
    )
    assert conv_in.title == "Daily Practice"
    assert conv_in.target_language == "en"
    assert conv_in.topic == "Travel"

    conv_update = ConversationUpdate(title="  Updated  ", is_archived=True)
    assert conv_update.title == "Updated"
    assert conv_update.is_archived is True

    with pytest.raises(ValidationError):
        ConversationCreate(title="   ")

    with pytest.raises(ValidationError):
        ConversationUpdate(topic="   ")

    with pytest.raises(ValidationError):
        MessageCreate(content="   ")

    ai_resp = AIChatResponse(reply="Hello!", feedback="Great start.", suggested_title="Greeting")
    assert ai_resp.reply == "Hello!"
