"""S3 storage backend.

Auto-configures from environment variables (or a matrx_utils settings object):

    AWS_ACCESS_KEY_ID       — required
    AWS_SECRET_ACCESS_KEY   — required
    AWS_REGION              — optional, defaults to "us-east-1"
    AWS_S3_DEFAULT_BUCKET   — optional default bucket when none is supplied in
                              the URI (s3://path/key vs s3://bucket/path/key)

Path convention expected by this backend:
    "bucket-name/path/to/object.ext"

If AWS_S3_DEFAULT_BUCKET is set you may omit the bucket segment:
    "path/to/object.ext"  →  "{default_bucket}/path/to/object.ext"
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any

from .base_backend import StorageBackend

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import CompletedPartTypeDef


_MULTIPART_THRESHOLD: int = 8 * 1024 * 1024  # 8 MB


class S3Backend(StorageBackend):
    def __init__(self) -> None:
        self._client: S3Client | None = None
        self._default_bucket: str = ""
        self._region: str = "us-east-1"
        self._configured: bool = False
        self._init_from_settings()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _init_from_settings(self) -> None:
        try:
            from matrx_utils.conf import settings

            key_id: str = self._safe_get(settings, "AWS_ACCESS_KEY_ID")
            secret: str = self._safe_get(settings, "AWS_SECRET_ACCESS_KEY")
            if not key_id or not secret:
                return

            self._region = self._safe_get(settings, "AWS_REGION") or "us-east-1"
            self._default_bucket = self._safe_get(settings, "AWS_S3_DEFAULT_BUCKET") or ""
            self._configured = True
        except Exception:
            return

    @staticmethod
    def _safe_get(settings_obj: object, name: str) -> str:
        try:
            val: object = getattr(settings_obj, name, None)
            return val if isinstance(val, str) and val.strip() else ""
        except Exception:
            return ""

    def _get_client(self) -> S3Client:
        """Return the boto3 S3 client, creating it on first call."""
        if self._client is None:
            import boto3
            from matrx_utils.conf import settings

            self._client = boto3.client(  # type: ignore[assignment]
                "s3",
                region_name=self._region,
                aws_access_key_id=self._safe_get(settings, "AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=self._safe_get(settings, "AWS_SECRET_ACCESS_KEY"),
            )
        return self._client  # type: ignore[return-value]

    def is_configured(self) -> bool:
        return self._configured

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _parse_path(self, path: str) -> tuple[str, str]:
        """Split 'bucket/key/path' → ('bucket', 'key/path').

        If the path does not contain a '/' the entire string is treated as
        the key and the default bucket is used.
        """
        if "/" in path:
            bucket, _, key = path.partition("/")
            if not key:
                raise ValueError(f"S3 path '{path}' has no key component after the bucket.")
            return bucket, key
        if self._default_bucket:
            return self._default_bucket, path
        raise ValueError(
            f"Cannot resolve S3 path '{path}': no bucket specified and "
            "AWS_S3_DEFAULT_BUCKET is not set."
        )

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def read(self, path: str) -> bytes:
        self._require_configured()
        bucket, key = self._parse_path(path)
        response: Any = self._get_client().get_object(Bucket=bucket, Key=key)
        body: bytes = response["Body"].read()
        return body

    def write(self, path: str, content: bytes | str, acl: str = "private") -> bool:
        self._require_configured()
        bucket, key = self._parse_path(path)
        client: S3Client = self._get_client()

        raw: bytes = content.encode() if isinstance(content, str) else content

        if len(raw) >= _MULTIPART_THRESHOLD:
            self._multipart_upload(client, bucket, key, raw, acl)
        else:
            client.put_object(Bucket=bucket, Key=key, Body=raw, ACL=acl)  # type: ignore[arg-type]
        return True

    def _multipart_upload(
        self,
        client: S3Client,
        bucket: str,
        key: str,
        content: bytes,
        acl: str,
    ) -> None:
        mpu: Any = client.create_multipart_upload(Bucket=bucket, Key=key, ACL=acl)  # type: ignore[arg-type]
        upload_id: str = mpu["UploadId"]
        parts: list[CompletedPartTypeDef] = []
        chunk_size: int = _MULTIPART_THRESHOLD
        try:
            for i, offset in enumerate(range(0, len(content), chunk_size), start=1):
                chunk: bytes = content[offset : offset + chunk_size]
                part: Any = client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=i,
                    UploadId=upload_id,
                    Body=chunk,
                )
                parts.append({"PartNumber": i, "ETag": part["ETag"]})
            client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
        except Exception:
            client.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)
            raise

    def append(self, path: str, content: bytes | str) -> bool:
        self._require_configured()
        try:
            existing: bytes = self.read(path)
        except Exception:
            existing = b""

        raw: bytes = content.encode() if isinstance(content, str) else content
        return self.write(path, existing + raw)

    def delete(self, path: str) -> bool:
        self._require_configured()
        bucket, key = self._parse_path(path)
        self._get_client().delete_object(Bucket=bucket, Key=key)
        return True

    # ------------------------------------------------------------------
    # URL generation
    # ------------------------------------------------------------------

    def get_url(self, path: str, expires_in: int = 3600) -> str:
        self._require_configured()
        bucket, key = self._parse_path(path)
        url: str = self._get_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return url

    def make_public_url(self, path: str) -> str:
        """Return the permanent public URL (only works for public-read objects)."""
        bucket, key = self._parse_path(path)
        return f"https://{bucket}.s3.{self._region}.amazonaws.com/{key}"

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_files(self, prefix: str = "") -> list[str]:
        self._require_configured()
        client: S3Client = self._get_client()
        bucket: str
        key_prefix: str

        if "/" in prefix:
            bucket, _, key_prefix = prefix.partition("/")
        elif self._default_bucket:
            bucket = self._default_bucket
            key_prefix = prefix
        else:
            raise ValueError(
                f"Cannot list S3 files for prefix '{prefix}': "
                "no bucket specified and AWS_S3_DEFAULT_BUCKET is not set."
            )

        paginator: Any = client.get_paginator("list_objects_v2")
        results: list[str] = []
        for page in paginator.paginate(Bucket=bucket, Prefix=key_prefix):
            for obj in page.get("Contents", []):
                results.append(f"{bucket}/{obj['Key']}")
        return results

    # ------------------------------------------------------------------
    # Copy / move helpers (convenience, not in ABC)
    # ------------------------------------------------------------------

    def copy(self, src_path: str, dst_path: str) -> bool:
        """Server-side copy within S3 — no data transfer to/from client."""
        self._require_configured()
        src_bucket, src_key = self._parse_path(src_path)
        dst_bucket, dst_key = self._parse_path(dst_path)
        self._get_client().copy_object(
            CopySource={"Bucket": src_bucket, "Key": src_key},
            Bucket=dst_bucket,
            Key=dst_key,
        )
        return True

    def get_metadata(self, path: str) -> dict[str, Any]:
        """Return object metadata (content-type, size, last-modified, etc.)."""
        self._require_configured()
        bucket, key = self._parse_path(path)
        response: Any = self._get_client().head_object(Bucket=bucket, Key=key)
        return {
            "content_type": response.get("ContentType", ""),
            "size": response.get("ContentLength", 0),
            "last_modified": str(response.get("LastModified", "")),
            "etag": response.get("ETag", "").strip('"'),
            "metadata": response.get("Metadata", {}),
        }

    def upload_file(self, local_path: str, s3_path: str, acl: str = "private") -> bool:
        """Upload a local file to S3 using streaming (memory-efficient)."""
        self._require_configured()
        bucket, key = self._parse_path(s3_path)
        self._get_client().upload_file(local_path, bucket, key, ExtraArgs={"ACL": acl})
        return True

    def download_file(self, s3_path: str, local_path: str) -> bool:
        """Download an S3 object to a local file path."""
        self._require_configured()
        bucket, key = self._parse_path(s3_path)
        self._get_client().download_file(bucket, key, local_path)
        return True

    def upload_fileobj(self, file_obj: io.IOBase, s3_path: str, acl: str = "private") -> bool:
        """Upload a file-like object to S3."""
        self._require_configured()
        bucket, key = self._parse_path(s3_path)
        self._get_client().upload_fileobj(file_obj, bucket, key, ExtraArgs={"ACL": acl})
        return True
