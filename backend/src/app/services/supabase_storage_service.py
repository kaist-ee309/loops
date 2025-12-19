from __future__ import annotations

from urllib.parse import quote

from app.config import settings
from app.core.security import get_supabase_admin_client


class SupabaseStorageService:
    @staticmethod
    def public_url(bucket: str, path: str) -> str:
        # Ensure safe URL path while preserving slashes
        encoded_path = "/".join(quote(p) for p in path.split("/"))
        return f"{settings.supabase_url}/storage/v1/object/public/{bucket}/{encoded_path}"

    @staticmethod
    def upload_bytes(*, bucket: str, path: str, data: bytes, mime_type: str) -> str:
        supabase = get_supabase_admin_client()

        # Upsert so reruns of the batch are idempotent.
        supabase.storage.from_(bucket).upload(
            path=path,
            file=data,
            file_options={
                "content-type": mime_type,
                "upsert": True,
            },
        )

        return SupabaseStorageService.public_url(bucket=bucket, path=path)
