"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_id, get_current_active_user_id
from app.schemas.auth import Token, LoginRequest, RegisterRequest
from app.schemas.user import User
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new user."""
    auth_service = AuthService(db)

    try:
        user = await auth_service.create_user(
            email=request.email,
            password=request.password,
        )
        return User.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login user and return access token."""
    auth_service = AuthService(db)

    try:
        token = await auth_service.login(
            email=request.email,
            password=request.password,
        )
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """OAuth2 compatible token login."""
    auth_service = AuthService(db)

    try:
        token = await auth_service.login(
            email=form_data.username,
            password=form_data.password,
        )
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=User)
async def get_current_user_info(
    user_id: str = Depends(get_current_active_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user information."""
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return User.model_validate(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Refresh access token."""
    from datetime import timedelta
    from app.core.security import create_access_token

    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=timedelta(hours=24),
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,
    )


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}
