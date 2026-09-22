"""Authentication and user management business logic service."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserLogin, UserRegister

security_scheme = HTTPBearer()


async def register_user(db: AsyncSession, user_in: UserRegister) -> User:
    """Register a new user in the system after checking for existing email.

    Args:
        db (AsyncSession): Database session.
        user_in (UserRegister): User registration data payload.

    Returns:
        User: Created User ORM instance.

    Raises:
        HTTPException: 400 Bad Request if email address is already registered.
    """
    # Check if email is already taken
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    # Hash password and store user
    hashed_pwd = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role.value
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> Token:
    """Authenticate user credentials and issue a signed JWT access token.

    Args:
        db (AsyncSession): Database session.
        credentials (UserLogin): User login credentials (email & password).

    Returns:
        Token: JWT access token response payload.

    Raises:
        HTTPException: 401 Unauthorized if email or password is incorrect.
    """
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email address or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.email,
        role=user.role,
        user_id=user.id
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name
    )


async def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """FastAPI dependency to retrieve the currently authenticated user from Bearer token.

    Args:
        auth_credentials (HTTPAuthorizationCredentials): Bearer token from authorization header.
        db (AsyncSession): Database session.

    Returns:
        User: Authenticated User ORM object.

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or user not found.
    """
    token = auth_credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_provider(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency ensuring current user has provider role.

    Args:
        current_user (User): Authenticated user.

    Returns:
        User: Provider User ORM object.

    Raises:
        HTTPException: 403 Forbidden if user is not a service provider.
    """
    if current_user.role != UserRole.PROVIDER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Only service providers can perform this operation."
        )
    return current_user


async def get_current_customer(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency rendering current user customer check.

    Args:
        current_user (User): Authenticated user.

    Returns:
        User: Customer User ORM object.

    Raises:
        HTTPException: 403 Forbidden if user is not a customer.
    """
    if current_user.role != UserRole.CUSTOMER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Only customers can perform this operation."
        )
    return current_user
