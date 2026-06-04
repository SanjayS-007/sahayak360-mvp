"""
Authentication routes — login, register, profile.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt_handler import create_access_token
from auth.password import hash_password, verify_password
from auth.dependencies import get_current_user
from config import settings
from db.postgres import get_db
from db.models import User

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role: str = Field(..., pattern=r"^(teacher|student|admin|parent)$")
    user_id: str = Field(..., pattern=r"^(TCH|STU|ADM)-\d{2,8}$")
    institution_id: str = Field(default=None)
    department_id: str = Field(default=None)
    class_section: str = Field(default=None)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str
    class_section: str | None = None


class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    class_section: str | None = None
    department_id: str | None = None


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check existing email
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Check existing user_id
    existing_id = await db.execute(select(User).where(User.user_id == req.user_id))
    if existing_id.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User ID already taken")

    user = User(
        user_id=req.user_id,
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        department_id=req.department_id,
        class_section=req.class_section,
    )
    db.add(user)
    await db.flush()

    token = create_access_token(
        {"sub": user.user_id, "role": user.role},
        timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        user_id=user.user_id,
        role=user.role,
        full_name=user.full_name,
        class_section=user.class_section,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = create_access_token(
        {"sub": user.user_id, "role": user.role},
        timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
    )
    return TokenResponse(
        access_token=token,
        user_id=user.user_id,
        role=user.role,
        full_name=user.full_name,
        class_section=user.class_section,
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(user: User = Depends(get_current_user)):
    return UserProfile(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        class_section=user.class_section,
        department_id=user.department_id,
    )
