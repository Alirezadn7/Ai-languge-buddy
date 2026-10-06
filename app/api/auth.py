from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import hash_password

router = APIRouter(prefix="/auth" , tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    
    existing_user = await db.scalar(
        select(User).where(User.email == user_in.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The entered email has already been registered.",
        )

    
    try:
        hashed_pwd = hash_password(user_in.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    #  Create the user with the default language profile
    profile_data = user_in.profile.model_dump() if user_in.profile else {}
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        profile=UserProfile(**profile_data),
    )


    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The entered email has already been registered.",
        )
    await db.refresh(new_user, attribute_names=["profile"])

    return new_user