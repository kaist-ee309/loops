from __future__ import annotations

import asyncio
import hashlib
import time
from collections import deque
from math import ceil
from typing import Literal
from uuid import UUID

from fastapi import HTTPException, status
from openai import AsyncOpenAI

from app.config import settings
from app.core.exceptions import ExternalServiceError

AudioFormat = Literal["mp3", "ogg"]
OpenAIResponseFormat = Literal["mp3", "opus"]


class TTSService:
    """Text-to-Speech service wrapper.

    Current implementation:
    - Provider: OpenAI TTS
    - Cache: in-memory TTL
    - Rate limiting: in-memory sliding window per user

    Notes:
    - In-memory caching/limiting is single-process only.
    - For multi-instance deployments, switch to Redis.
    """

    _cache: dict[str, tuple[float, bytes]] = {}
    _rate_windows: dict[str, deque[float]] = {}
    _lock = asyncio.Lock()

    @staticmethod
    def _cache_key(*, text: str, voice: str, audio_format: AudioFormat, model: str) -> str:
        h = hashlib.sha256()
        h.update(model.encode("utf-8"))
        h.update(b"\x00")
        h.update(voice.encode("utf-8"))
        h.update(b"\x00")
        h.update(audio_format.encode("utf-8"))
        h.update(b"\x00")
        h.update(text.encode("utf-8"))
        return h.hexdigest()

    @classmethod
    async def generate_audio(
        cls,
        *,
        profile_id: UUID,
        text: str,
        audio_format: AudioFormat = "mp3",
        voice: str | None = None,
    ) -> bytes:
        """Generate audio bytes for given text.

        Raises:
        - HTTPException(429) when rate limited
        - ExternalServiceError(503) on provider failures
        """

        api_key = settings.openai_api_key
        if not api_key:
            raise ExternalServiceError("OpenAI API key is not configured", service="openai")

        model = settings.openai_tts_model
        chosen_voice = voice or settings.openai_tts_default_voice

        now = time.monotonic()
        cache_ttl = max(0, int(settings.tts_cache_ttl_seconds))
        cache_key = cls._cache_key(
            text=text,
            voice=chosen_voice,
            audio_format=audio_format,
            model=model,
        )

        async with cls._lock:
            # Cache hit
            cached = cls._cache.get(cache_key)
            if cached is not None:
                expires_at, audio_bytes = cached
                if expires_at > now:
                    return audio_bytes
                cls._cache.pop(cache_key, None)

            # Rate limit
            limit = max(1, int(settings.tts_rate_limit_requests))
            window = max(1, int(settings.tts_rate_limit_window_seconds))

            bucket_key = f"tts:{profile_id}"
            q = cls._rate_windows.get(bucket_key)
            if q is None:
                q = deque()
                cls._rate_windows[bucket_key] = q

            cutoff = now - window
            while q and q[0] <= cutoff:
                q.popleft()

            if len(q) >= limit:
                retry_after = ceil((q[0] + window) - now) if q else window
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="TTS rate limit exceeded",
                    headers={"Retry-After": str(max(1, retry_after))},
                )

            q.append(now)

            # Opportunistic cache pruning
            if len(cls._cache) > max(1, int(settings.tts_cache_max_entries)):
                cls._prune_cache_locked(now)

        # Provider call (outside lock)
        response_format: OpenAIResponseFormat = "mp3" if audio_format == "mp3" else "opus"

        try:
            client = AsyncOpenAI(api_key=api_key)
            response = await client.audio.speech.create(
                model=model,
                voice=chosen_voice,
                input=text,
                response_format=response_format,
            )
            audio_bytes = response.content
        except HTTPException:
            raise
        except Exception as e:
            raise ExternalServiceError("TTS generation failed", service="openai") from e

        # Store in cache
        expires_at = now + cache_ttl
        async with cls._lock:
            cls._cache[cache_key] = (expires_at, audio_bytes)
            if len(cls._cache) > max(1, int(settings.tts_cache_max_entries)):
                cls._prune_cache_locked(time.monotonic())

        return audio_bytes

    @classmethod
    def _prune_cache_locked(cls, now: float) -> None:
        # Remove expired first
        expired_keys = [k for k, (exp, _) in cls._cache.items() if exp <= now]
        for k in expired_keys:
            cls._cache.pop(k, None)

        # Hard cap fallback: drop arbitrary items until within limit
        max_entries = max(1, int(settings.tts_cache_max_entries))
        while len(cls._cache) > max_entries:
            cls._cache.pop(next(iter(cls._cache)))
