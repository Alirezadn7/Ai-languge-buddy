import pytest
from sqlalchemy import select

from app.models.chat import Conversation, Message, MessageRole
from app.models.user import LanguageLevel, User, UserProfile


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
