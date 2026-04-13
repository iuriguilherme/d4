import uuid
from datetime import timedelta, datetime, UTC

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, Cookie, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.app.core.database import get_db
from api.app.core.config import settings
from api.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from api.app.models.user import User
from api.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from api.app.dependencies.auth import get_current_user
from api.app.dependencies.session import get_session_id
from api.app.core.database import AsyncSessionLocal
from api.app.services.behavior import emit_event


async def _emit(user_id, event_type, data, session_id):
    async with AsyncSessionLocal() as bg_db:
        await emit_event(bg_db, user_id, event_type, data, session_id)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    session_id: uuid.UUID | None = Depends(get_session_id),
):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=int(timedelta(days=settings.refresh_token_expire_days).total_seconds()),
        path="/api/v1/auth/refresh",
    )

    background_tasks.add_task(
        _emit,
        user.id,
        "user_login",
        {"hour_of_day": datetime.now(UTC).hour, "day_of_week": datetime.now(UTC).weekday()},
        session_id,
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise JWTError("wrong type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.delete("/token", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
