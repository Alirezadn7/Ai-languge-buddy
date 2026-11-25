from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User

password_hash = PasswordHash.recommended()

# Used during authentication when an email does not exist so timing matches a real check.
DUMMY_HASH = password_hash.hash("dummypassword")


def hash_password(password: str) -> str:
    """Hash a plain-text password using the configured Argon2/pwdlib hasher."""
    if not password:
        raise ValueError("Password cannot be empty.")
    return password_hash.hash(password)


get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash, returning False on mismatch or invalid hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return password_hash.verify(plain_password, hashed_password)
    except (UnknownHashError, ValueError):
        return False


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Look up an active user by email and verify their password in constant-like time."""
    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token containing the given payload and expiration."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token; raises jwt.PyJWTError on invalid or expired tokens."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
