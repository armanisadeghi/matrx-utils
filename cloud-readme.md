# matrx-utils — Cloud Storage

Everything runs through `FileManager`. Never instantiate a backend directly in app code.

---

## Setup

### 1. Environment variables

Set the variables for whichever backends you use. Unconfigured backends are silently ignored — no errors until you actually call one.

```bash
# S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-2
AWS_S3_DEFAULT_BUCKET=my-bucket          # optional default

# Supabase (new key format — use one of the two)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SECRET_KEY=sb_secret_...        # preferred — backend / service-level
SUPABASE_PUBLISHABLE_KEY=sb_publishable_ # low-privilege, client-safe

# Legacy Supabase keys (still accepted, lower priority)
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_ANON_KEY=...

# Custom file server (optional)
FILE_SERVER_BASE_URL=https://files.myapp.com
FILE_SERVER_API_KEY=...
```

### 2. Instantiate

```python
from matrx_utils.file_handling import FileManager

fm = FileManager("my_service")

# Check what's live
print(fm.configured_backends())  # e.g. ['s3', 'supabase']
```

---

## URI format

All cloud paths use a URI scheme. The bucket is always explicit — there is no global default for Supabase.

```
s3://bucket-name/path/to/file.ext
supabase://bucket-name/path/to/file.ext
server://path/to/file.ext
```

---

## Core I/O — FileManager (use in FastAPI routes)

Always prefer the `_async` variants inside FastAPI. S3 uses `run_in_executor` (non-blocking), Supabase uses its native `AsyncClient`, and the custom server uses `httpx.AsyncClient`.

### Read

```python
# From a URI
raw: bytes = await fm.read_async("s3://bucket/report.pdf")
raw: bytes = await fm.read_async("supabase://bucket/users/123/avatar.png")

# From any URL the frontend sends (public, signed, expired — all handled)
raw: bytes = await fm.read_url_async(url_from_react)
```

### Write

```python
ok = await fm.write_async("s3://bucket/output.json", json_bytes)
ok = await fm.write_async("supabase://bucket/users/123/doc.pdf", pdf_bytes)
ok = await fm.write_async("supabase://bucket/log.txt", "text content")
```

### Append, Delete, List

```python
ok    = await fm.append_async("s3://bucket/log.txt", new_line)
ok    = await fm.delete_async("supabase://bucket/old-file.png")
files = await fm.list_files_async("s3://bucket/reports/")
```

### Signed / presigned URLs

```python
url = await fm.get_url_async("s3://bucket/private.pdf", expires_in=3600)
url = await fm.get_url_async("supabase://bucket/user/file.png", expires_in=300)
```

### Parallel I/O

```python
import asyncio

a, b, c = await asyncio.gather(
    fm.read_async("s3://bucket/a.pdf"),
    fm.read_async("supabase://bucket/b.txt"),
    fm.read_async("s3://bucket/c.csv"),
)
```

---

## ensure_url — smart URL refresh

Call this when a URL from long-lived storage (chat history, database record) might be stale. It reads the expiry **from the URL itself** — zero network calls when still fresh.

| URL type | How expiry is detected |
|---|---|
| Native URI (`s3://`, `supabase://`) | Always generates a fresh URL |
| Supabase signed URL | Decodes JWT `exp` claim from `?token=` |
| S3 presigned URL | Reads `X-Amz-Date` + `X-Amz-Expires` query params |
| Public HTTPS (no expiry) | Returned as-is |

```python
# In a FastAPI route — safe to call every time, free when URL is fresh
url = await fm.ensure_url_async(url_from_db, expires_in=3600)

# Then pass to LLM or return to client
```

---

## LLM helpers

### get_for_llm — fetch a file in the format a provider needs

```python
# Provider fetches the URL directly (OpenAI vision, Gemini File API)
url = await fm.get_for_llm_async(file_url, mode="url", expires_in=300)
openai_client.chat.completions.create(messages=[{
    "role": "user",
    "content": [{"type": "image_url", "image_url": {"url": url}}]
}])

# Provider needs inline base64 (Anthropic, most multi-modal APIs)
b64 = await fm.get_for_llm_async(file_url, mode="base64")
anthropic_client.messages.create(messages=[{
    "role": "user",
    "content": [{"type": "image", "source": {
        "type": "base64", "media_type": "image/png", "data": b64
    }}]
}])

# Raw bytes (when you handle encoding yourself)
raw = await fm.get_for_llm_async(file_url, mode="bytes")
```

`file_url` can be anything the frontend sends — native URI, public HTTPS, signed, or expired.

### push_from_llm — store LLM-generated content

```python
result = await openai_client.images.generate(model="dall-e-3", ...)

# LLM returned base64
await fm.push_from_llm_async(
    result.data[0].b64_json,
    "supabase://bucket/users/123/generated.png",
    source_format="base64",
)

# LLM returned a temporary URL (DALL-E, Gemini)
await fm.push_from_llm_async(
    result.data[0].url,
    "s3://bucket/generated/image.png",
    source_format="url",
)

# LLM returned raw bytes
await fm.push_from_llm_async(audio_bytes, "s3://bucket/tts/clip.mp3", source_format="bytes")
```

---

## Cloud methods inside handlers

Every handler (`PDFHandler`, `ImageHandler`, etc.) built through `FileManager` automatically receives the same `BackendRouter` and exposes identical cloud methods prefixed with `cloud_`. Use these when writing pipeline logic inside a handler subclass.

```python
class MyHandler(FileHandler):
    async def process(self, url_from_client: str) -> bytes:
        # Read via credentials — works even if URL is expired
        raw = await self.cloud_read_url_async(url_from_client)

        # Ensure a URL is fresh before passing to an LLM
        fresh_url = await self.cloud_ensure_url_async(url_from_client)

        # Write result back to cloud
        await self.cloud_write_async("s3://bucket/output.bin", raw)

        # Full LLM helpers
        b64 = await self.get_for_llm_async(url_from_client, mode="base64")
        await self.push_from_llm_async(b64_response, "supabase://bucket/out.png")
```

Available methods on every handler:

| Method | Async version | Description |
|---|---|---|
| `cloud_read(uri)` | `cloud_read_async` | Read raw bytes from URI |
| `cloud_write(uri, content)` | `cloud_write_async` | Write bytes or str |
| `cloud_append(uri, content)` | `cloud_append_async` | Append to object |
| `cloud_delete(uri)` | `cloud_delete_async` | Delete object |
| `cloud_get_url(uri)` | `cloud_get_url_async` | Signed/presigned URL |
| `cloud_list_files(prefix)` | `cloud_list_files_async` | List under prefix |
| `cloud_read_url(url)` | `cloud_read_url_async` | Read from any URL format |
| `cloud_ensure_url(url)` | `cloud_ensure_url_async` | Refresh if expired |
| `get_for_llm(url, mode)` | `get_for_llm_async` | Fetch for LLM provider |
| `push_from_llm(data, uri)` | `push_from_llm_async` | Store LLM output |

---

## ImageHandler cloud methods

`ImageHandler` adds higher-level helpers that work with PIL `Image` objects directly:

```python
# Decode base64 → write to cloud (no intermediate local file)
await image_handler.base64_to_cloud_async(b64_string, "s3://bucket/avatar.png")

# Fetch from cloud → PIL Image
img = await image_handler.read_image_from_cloud_async("supabase://bucket/photo.jpg")
img_resized = img.resize((256, 256))

# PIL Image → encode → upload
await image_handler.write_image_to_cloud_async(img_resized, "s3://bucket/thumb.webp", fmt="WEBP")
```

---

## PDFHandler pipeline

`PdfPipelineOptions.upload_result_to` accepts any cloud URI prefix. The extracted text is uploaded after processing.

```python
from matrx_utils.file_handling.specific_handlers.pdf_handler import (
    PDFHandler, PdfPipelineOptions
)

handler = PDFHandler("my_service")
handler.set_cloud_router(fm.cloud)  # or construct via FileManager

result = await handler.full_pipeline(
    source="https://signed-url-or-local-path/doc.pdf",
    options=PdfPipelineOptions(
        extract_text=True,
        chunk_and_process_with_ai=True,
        upload_result_to="supabase://bucket/pdf_results/",
    ),
    ai_processor=my_async_ai_fn,
)

print(result.raw_text)    # extracted text
print(result.cloud_uri)   # where it was uploaded, e.g. supabase://bucket/pdf_results/<uuid>.txt
```

---

## Async strategy per backend

| Backend | Async implementation | Notes |
|---|---|---|
| S3 | `run_in_executor` (thread pool) | boto3 is sync; thread pool is genuinely non-blocking to the event loop — standard production pattern |
| Supabase | Native `AsyncClient` (`acreate_client`) | True async, no thread pool |
| Custom server | `httpx.AsyncClient` | True async |

---

## Direct backend access (advanced)

For operations not exposed on `FileManager`, the raw backends are accessible:

```python
s3  = fm.cloud.s3        # S3Backend
sup = fm.cloud.supabase  # SupabaseBackend
srv = fm.cloud.server    # ServerBackend

# S3-specific
buckets = s3.list_buckets()
s3.copy("bucket/src.txt", "bucket/dst.txt")
meta = s3.get_metadata("bucket/file.pdf")
s3.upload_file("/local/large.zip", "bucket/archive.zip")

# Supabase-specific
buckets = sup.list_buckets()
pub_url = sup.get_public_url("bucket/public-asset.png")
await sup.copy_async("bucket/src.png", "bucket/dst.png")
```
