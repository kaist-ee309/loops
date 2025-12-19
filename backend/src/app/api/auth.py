"""
인증 관련 API 엔드포인트.

Supabase Auth를 사용한 회원가입, 로그인, 토큰 갱신, 로그아웃 기능을 제공합니다.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.core.security import get_supabase_client
from app.database import get_session
from app.models import Profile, ProfileRead
from app.services.profile_service import ProfileService

TAG = "authentication"
TAG_METADATA = {
    "name": TAG,
    "description": "인증 관련 API. 회원가입, 로그인, 토큰 갱신, 로그아웃 등 Supabase Auth를 통한 사용자 인증을 처리합니다.",
}

router = APIRouter(prefix="/auth", tags=[TAG])


class RegisterRequest(BaseModel):
    """회원가입 요청 스키마."""

    email: EmailStr = Field(
        description="사용자 이메일 주소. 로그인 시 사용되며 중복 불가",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=255,
        description="비밀번호. 최소 8자 이상",
        examples=["securePassword123!"],
    )


class LoginRequest(BaseModel):
    """로그인 요청 스키마."""

    email: EmailStr = Field(
        description="가입 시 사용한 이메일 주소",
        examples=["user@example.com"],
    )
    password: str = Field(
        max_length=255,
        description="비밀번호",
        examples=["securePassword123!"],
    )


class AuthResponse(BaseModel):
    """인증 응답 스키마."""

    access_token: str = Field(
        description="API 요청 시 사용할 JWT 액세스 토큰. Authorization 헤더에 Bearer 토큰으로 포함"
    )
    refresh_token: str = Field(description="액세스 토큰 갱신 시 사용할 리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입. 항상 'bearer'")
    profile: ProfileRead = Field(description="인증된 사용자 프로필 정보")


class RefreshRequest(BaseModel):
    """토큰 갱신 요청 스키마."""

    refresh_token: str = Field(
        description="로그인 시 발급받은 리프레시 토큰",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다. Supabase Auth를 통해 인증 정보가 관리됩니다.",
    responses={
        201: {"description": "회원가입 성공. 액세스 토큰과 프로필 정보 반환"},
        400: {"description": "잘못된 요청 - 이메일 중복 또는 유효하지 않은 데이터"},
        422: {"description": "유효성 검사 실패 - 필수 필드 누락 또는 형식 오류"},
    },
)
async def register(
    request: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthResponse:
    """
    새로운 사용자를 등록합니다.

    **처리 과정:**
    1. Supabase Auth에 계정 생성
    2. 로컬 데이터베이스에 프로필 정보 저장
    3. 액세스 토큰 및 리프레시 토큰 발급

    **주의사항:**
    - 이메일은 Supabase에서 고유해야 합니다
    - 비밀번호는 최소 8자 이상이어야 합니다
    """
    supabase = get_supabase_client()

    # Register user in Supabase Auth
    try:
        auth_response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user in Supabase",
        )

    # Create profile in our database using Supabase user ID as the profile ID
    profile = await ProfileService.create_profile(
        session,
        profile_id=UUID(auth_response.user.id),
    )

    return AuthResponse(
        access_token=auth_response.session.access_token,
        refresh_token=auth_response.session.refresh_token,
        profile=ProfileRead.model_validate(profile),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="로그인",
    description="이메일과 비밀번호로 로그인하여 액세스 토큰을 발급받습니다.",
    responses={
        200: {"description": "로그인 성공. 액세스 토큰과 프로필 정보 반환"},
        401: {"description": "인증 실패 - 이메일 또는 비밀번호가 잘못됨"},
        404: {"description": "프로필을 찾을 수 없음 - Supabase에는 있지만 로컬 DB에 없는 경우"},
        422: {"description": "유효성 검사 실패 - 이메일 형식 오류 등"},
    },
)
async def login(
    request: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthResponse:
    """
    이메일과 비밀번호로 로그인합니다.

    **처리 과정:**
    1. Supabase Auth로 인증 검증
    2. 로컬 데이터베이스에서 프로필 정보 조회
    3. 액세스 토큰 및 리프레시 토큰 반환

    **반환되는 토큰 사용법:**
    - `access_token`: API 요청 시 `Authorization: Bearer {access_token}` 헤더에 포함
    - `refresh_token`: 액세스 토큰 만료 시 `/auth/refresh`로 갱신
    """
    supabase = get_supabase_client()

    # Authenticate with Supabase
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password,
            }
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get profile from our database
    profile = await ProfileService.get_profile(session, UUID(auth_response.user.id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found in database",
        )

    return AuthResponse(
        access_token=auth_response.session.access_token,
        refresh_token=auth_response.session.refresh_token,
        profile=ProfileRead.model_validate(profile),
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.",
    responses={
        200: {"description": "토큰 갱신 성공. 새로운 액세스 토큰과 리프레시 토큰 반환"},
        401: {"description": "인증 실패 - 리프레시 토큰이 유효하지 않거나 만료됨"},
        404: {"description": "프로필을 찾을 수 없음"},
    },
)
async def refresh_token(
    request: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthResponse:
    """
    리프레시 토큰으로 새 액세스 토큰을 발급받습니다.

    **사용 시점:**
    - 액세스 토큰이 만료되었을 때
    - 클라이언트에서 401 응답을 받았을 때

    **주의사항:**
    - 리프레시 토큰도 만료될 수 있습니다
    - 리프레시 토큰이 만료되면 다시 로그인해야 합니다
    """
    supabase = get_supabase_client()

    try:
        auth_response = supabase.auth.refresh_session(request.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get profile from our database
    profile = await ProfileService.get_profile(session, UUID(auth_response.user.id))
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found in database",
        )

    return AuthResponse(
        access_token=auth_response.session.access_token,
        refresh_token=auth_response.session.refresh_token,
        profile=ProfileRead.model_validate(profile),
    )


@router.post(
    "/logout",
    summary="로그아웃",
    description="현재 사용자를 로그아웃합니다.",
    responses={
        200: {"description": "로그아웃 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def logout(
    current_profile: CurrentActiveProfile,
) -> dict[str, str]:
    """
    현재 사용자를 로그아웃합니다.

    **주의사항:**
    - 서버에서는 성공 응답만 반환합니다
    - 실제 토큰 무효화는 클라이언트에서 처리해야 합니다
    - 클라이언트는 저장된 토큰을 삭제해야 합니다
    """
    # Supabase handles token invalidation on client side
    # Server-side we just return success
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=ProfileRead,
    summary="현재 사용자 정보 조회",
    description="인증된 현재 사용자의 프로필 정보를 반환합니다.",
    responses={
        200: {"description": "현재 사용자 프로필 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_current_user(
    current_profile: CurrentActiveProfile,
) -> Profile:
    """
    현재 인증된 사용자의 프로필 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - 사용자 ID (UUID)
    - 학습 설정 (일일 목표, 테마 등)
    - 스트릭 정보 (현재/최장 연속 학습일)
    - 계정 생성일 및 수정일
    """
    return current_profile
