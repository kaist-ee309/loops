"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import verify_supabase_token
from app.database import get_session
from app.models import Profile
from app.services.profile_service import ProfileService

# HTTPBearer scheme for token extraction from Authorization header
security = HTTPBearer()


async def get_current_profile(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Profile:
    """
    Get the current authenticated user's profile from Supabase JWT token.

    Args:
        credentials: Bearer token from Authorization header
        session: Database session

    Returns:
        Profile object of authenticated user

    Raises:
        HTTPException: If token is invalid or profile not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify Supabase token and get user id
    supabase_uid = verify_supabase_token(credentials.credentials)
    if supabase_uid is None:
        raise credentials_exception

    # Get profile from database by Supabase UID (which is the profile ID)
    profile = await ProfileService.get_profile(session, UUID(supabase_uid))
    if profile is None:
        raise credentials_exception

    return profile


async def get_current_active_profile(
    current_profile: Annotated[Profile, Depends(get_current_profile)],
) -> Profile:
    """
    Get the current active profile.

    Args:
        current_profile: Profile from get_current_profile dependency

    Returns:
        Profile object (profiles don't have is_active field, so just return as-is)
    """
    return current_profile


# Type aliases for cleaner dependency injection
CurrentProfile = Annotated[Profile, Depends(get_current_profile)]
CurrentActiveProfile = Annotated[Profile, Depends(get_current_active_profile)]
