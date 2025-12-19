"""
Security utilities for Supabase token verification.
"""

from supabase import Client, create_client

from app.config import settings

# Supabase client with publishable key (for auth operations)
_supabase_client: Client | None = None
# Supabase client with secret key (for admin/storage operations)
_supabase_admin_client: Client | None = None


def get_supabase_client() -> Client:
    """Get Supabase client with publishable key for auth operations."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_publishable_key,
        )
    return _supabase_client


def get_supabase_admin_client() -> Client:
    """Get Supabase client with secret key for admin/storage operations."""
    global _supabase_admin_client
    if _supabase_admin_client is None:
        if not settings.supabase_secret_key:
            raise RuntimeError("Missing SUPABASE_SECRET_KEY (settings.supabase_secret_key)")
        _supabase_admin_client = create_client(
            settings.supabase_url,
            settings.supabase_secret_key,
        )
    return _supabase_admin_client


def verify_supabase_token(token: str) -> str | None:
    """
    Verify a Supabase token using the Supabase client.

    Args:
        token: The JWT token from Authorization header

    Returns:
        Supabase user ID if valid, None if invalid
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.get_user(token)
        if response and response.user:
            return response.user.id
        return None
    except Exception:
        return None
