from __future__ import annotations

from dataclasses import dataclass

from google import genai
from google.genai import types

from app.config import settings


@dataclass(frozen=True)
class GeneratedImage:
    bytes: bytes
    mime_type: str


class GeminiImageService:
    @staticmethod
    def generate_image(prompt: str, model: str | None = None) -> GeneratedImage:
        """Generate a single image from text prompt.

        Uses Gemini Developer API (API key) via google-genai SDK.
        """
        api_key = settings.gemini_api_key
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY (settings.gemini_api_key)")

        model_id = model or settings.gemini_image_model

        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=model_id,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )

        for part in response.parts:
            if part.inline_data is None:
                continue
            mime_type = part.inline_data.mime_type or "image/png"
            data = part.inline_data.data
            if not data:
                continue
            return GeneratedImage(bytes=data, mime_type=mime_type)

        raise RuntimeError("Gemini image generation returned no inline image data")
