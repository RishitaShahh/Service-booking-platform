"""API Router for authentication and user account management endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserOut
from app.services.auth_service import authenticate_user, get_current_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new User",
    description="Registers a new customer or service provider account."
)
async def register(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> UserOut:
    """Register a new user account.

    Args:
        user_in (UserRegister): Account registration details.
        db (AsyncSession): Database session.

    Returns:
        UserOut: Registered User profile object.
    """
    user = await register_user(db, user_in)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate User and retrieve JWT Token",
    description="Authenticates email and password credentials and issues a signed JWT access token."
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Authenticate credentials and generate token.

    Args:
        credentials (UserLogin): User login credentials.
        db (AsyncSession): Database session.

    Returns:
        Token: Access token response payload.
    """
    token = await authenticate_user(db, credentials)
    return token


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
    description="Retrieves profile information for the currently authenticated user."
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Retrieve profile of authenticated user.

    Args:
        current_user (User): Current user injected via Bearer token dependency.

    Returns:
        UserOut: User profile details.
    """
    return current_user
