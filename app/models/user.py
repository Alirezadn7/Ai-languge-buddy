from enum import StrEnum
from datetime import datetime, timezone
from sqlalchemy import DateTime , Enum, ForeignKey , Integer , String ,func
from sqlalchemy.orm import Mapped , mapped_column , relationship

from app.database import Base

class LanguageLevel(StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer , primary_key=True , index=True)
    email: Mapped[str] = mapped_column(String(255) , unique=True , index=True , nullable=False)
    hashed_password : Mapped[str] = mapped_column(String(255) , nullable=False)
    is_active : Mapped[bool] = mapped_column(default=True , nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(), # Automatically set creation timestamp by the database
        nullable=False,
    )
    
    # 1-to-1 relationship with UserProfile
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    
class UserProfile(Base):
    __tablename__ = "user_profiles" 
    
    id: Mapped[int] = mapped_column(Integer , primary_key=True , index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id" , ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    native_language: Mapped[str] = mapped_column(String(50) , default="fa")
    target_language: Mapped[str] = mapped_column(String(50) , default="en")
    
    level: Mapped[LanguageLevel] = mapped_column(
        Enum(LanguageLevel),
        default=LanguageLevel.A1,
        nullable=False,
    )
    
    user: Mapped["User"] = relationship("User" , back_populates="profile")
    
    