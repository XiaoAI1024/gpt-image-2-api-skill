#!/usr/bin/env python3
"""Generate or edit images through an OpenAI-compatible Images API."""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "auto"
DEFAULT_OUTPUT = "generated-image.png"
DEFAULT_TIMEOUT = 300
RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504, 524}
BASE_URL_ENV_NAMES = (
    "GPT_IMAGE_2_BASE_URL",
)
API_KEY_ENV_NAMES = (
    "BASE_URL_API_KEY",
)


def env_value(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def api_url(base_url: str, operation: str) -> str:
    base = base_url.strip().rstrip("/")
    if not re.match(r"^https?://", base, re.IGNORECASE):
        raise RuntimeError("Image API base URL must start with http:// or https://")
    if operation not in {"generations", "edits"}:
        raise RuntimeError(f"Unsupported image operation: {operation}")
    if base.endswith(f"/v1/images/{operation}"):
        return base
    if base.endswith("/v1/images"):
        return f"{base}/{operation}"
    if base.endswith("/v1"):
        return f"{base}/images/{operation}"
    return f"{base}/v1/images/{operation}"


def build_image_payload(
    *,
    model: str,
    prompt: str,
    size: str,
    quality: str,
    output_format: str | None,
    output_compression: int | None,
    moderation: str | None,
    response_format: str | None,
) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
    }
    optional_values = {
        "output_format": output_format,
        "output_compression": output_compression,
        "moderation": moderation,
        "response_format": response_format,
    }
    for key, value in optional_values.items():
        if value is not None and value != "":
            payload[key] = value
    return payload


def is_url(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https"}


def filename_from_url(url: str, fallback: str) -> str:
    name = Path(urlparse(url).path).name
    return name or fallback


def download_url(url: str, timeout: int) -> bytes:
    request = Request(url, headers={"User-Agent": "gpt-image-2-api-skill/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def file_part_from_source(source: str, timeout: int) -> tuple[str, str, bytes]:
    if is_url(source):
        filename = filename_from_url(source, "image.png")
        data = download_url(source, timeout)
    else:
        path = Path(source).expanduser()
        if not path.exists():
            raise RuntimeError(f"Input image does not exist: {source}")
        filename = path.name
        data = path.read_bytes()
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return filename, content_type, data


def append_form_field(body: bytearray, boundary: str, name: str, value: str) -> None:
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
    )
    body.extend(str(value).encode("utf-8"))
    body.extend(b"\r\n")


def append_file_field(
    body: bytearray,
    boundary: str,
    name: str,
    filename: str,
    content_type: str,
    data: bytes,
) -> None:
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="{name}"; '
            f'filename="{filename}"\r\n'
        ).encode("utf-8")
    )
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    body.extend(data)
    body.extend(b"\r\n")


def build_edit_multipart(
    *,
    fields: dict,
    images: list[str],
    mask: str | None,
    timeout: int,
) -> tuple[bytes, str]:
    if not images:
        raise RuntimeError("At least one --image is required for image edits.")

    boundary = f"----gpt-image-2-api-skill-{uuid.uuid4().hex}"
    body = bytearray()
    for key, value in fields.items():
        if value is not None and value != "":
            append_form_field(body, boundary, key, str(value))

    for index, image_source in enumerate(images, start=1):
        filename, content_type, data = file_part_from_source(image_source, timeout)
        if filename == "image.png" and len(images) > 1:
            filename = f"image-{index}.png"
        append_file_field(body, boundary, "image[]", filename, content_type, data)

    if mask:
        filename, content_type, data = file_part_from_source(mask, timeout)
        append_file_field(body, boundary, "mask", filename, content_type, data)

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def error_message_from_body(body: bytes) -> str:
    if not body:
        return ""
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return body.decode("utf-8", errors="replace")[:1000]
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if message:
                return str(message)
        if isinstance(error, str):
            return error
    return json.dumps(payload, ensure_ascii=False)[:1000]


def request_bytes(
    *,
    url: str,
    data: bytes,
    headers: dict,
    timeout: int,
    retries: int,
    retry_delay: float,
) -> bytes:
    last_error = None
    for attempt in range(retries + 1):
        request = Request(url, data=data, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as exc:
            body = exc.read()
            last_error = f"HTTP {exc.code}: {error_message_from_body(body)}"
            if exc.code not in RETRYABLE_HTTP_STATUSES or attempt >= retries:
                raise RuntimeError(last_error)
        except URLError as exc:
            last_error = f"Network error: {exc.reason}"
            if attempt >= retries:
                raise RuntimeError(last_error)
        if retry_delay > 0:
            time.sleep(retry_delay)
    raise RuntimeError(last_error or "API request failed")


def request_json(
    *,
    url: str,
    payload: dict,
    api_key: str,
    timeout: int,
    retries: int,
    retry_delay: float,
) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response_body = request_bytes(
        url=url,
        data=body,
        headers=headers,
        timeout=timeout,
        retries=retries,
        retry_delay=retry_delay,
    )
    return parse_json_response(response_body)


def request_multipart(
    *,
    url: str,
    body: bytes,
    content_type: str,
    api_key: str,
    timeout: int,
    retries: int,
    retry_delay: float,
) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": content_type,
    }
    response_body = request_bytes(
        url=url,
        data=body,
        headers=headers,
        timeout=timeout,
        retries=retries,
        retry_delay=retry_delay,
    )
    return parse_json_response(response_body)


def parse_json_response(body: bytes) -> dict:
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("API response was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("API response JSON must be an object")
    return payload


def image_object_candidates(response: dict) -> list[dict]:
    candidates = []
    if isinstance(response.get("data"), list):
        candidates.extend(item for item in response["data"] if isinstance(item, dict))
    if any(key in response for key in ("b64_json", "image_base64", "url")):
        candidates.append(response)
    return candidates


def extract_image_bytes(response: dict, timeout: int) -> bytes:
    for item in image_object_candidates(response):
        b64_image = item.get("b64_json") or item.get("image_base64")
        if isinstance(b64_image, str) and b64_image:
            try:
                return base64.b64decode(b64_image)
            except binascii.Error as exc:
                raise RuntimeError("Image b64_json was not valid base64") from exc

        image_url = item.get("url")
        if isinstance(image_url, str) and image_url:
            return download_url(image_url, timeout)

    raise RuntimeError("API response did not include data[0].b64_json or data[0].url")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be >= 0")
    return parsed


def compression_value(value: str) -> int:
    parsed = int(value)
    if parsed < 0 or parsed > 100:
        raise argparse.ArgumentTypeError("value must be from 0 to 100")
    return parsed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or edit images with gpt-image-2."
    )
    parser.add_argument("--prompt", required=True, help="Image prompt.")
    parser.add_argument(
        "--image",
        dest="images",
        action="append",
        default=[],
        help="Input image path or HTTP(S) URL for editing. Repeat for multi-image edits.",
    )
    parser.add_argument("--mask", help="Optional mask image path or HTTP(S) URL.")
    parser.add_argument(
        "--output",
        default=env_value("IMAGE_OUTPUT") or DEFAULT_OUTPUT,
        help="Output image path. Defaults to IMAGE_OUTPUT or generated-image.png.",
    )
    parser.add_argument(
        "--model",
        default=env_value("IMAGE_MODEL", "GPT_IMAGE_MODEL") or DEFAULT_MODEL,
        help="Image model. Defaults to gpt-image-2.",
    )
    parser.add_argument(
        "--size",
        default=env_value("IMAGE_SIZE", "GPT_IMAGE_SIZE") or DEFAULT_SIZE,
        help="Image size, such as 1024x1024 or auto.",
    )
    parser.add_argument(
        "--quality",
        choices=("auto", "low", "medium", "high"),
        default=env_value("IMAGE_QUALITY", "GPT_IMAGE_QUALITY") or DEFAULT_QUALITY,
        help="Image quality.",
    )
    parser.add_argument(
        "--output-format",
        choices=("png", "jpeg", "webp"),
        default=env_value("IMAGE_OUTPUT_FORMAT") or "png",
        help="Output format. Defaults to png.",
    )
    parser.add_argument(
        "--output-compression",
        type=compression_value,
        default=(
            compression_value(env_value("IMAGE_OUTPUT_COMPRESSION"))
            if env_value("IMAGE_OUTPUT_COMPRESSION")
            else None
        ),
        help="JPEG/WebP compression from 0 to 100.",
    )
    parser.add_argument(
        "--moderation",
        choices=("auto", "low"),
        default=env_value("IMAGE_MODERATION") or None,
        help="Moderation mode for supported image models.",
    )
    parser.add_argument(
        "--response-format",
        choices=("b64_json", "url"),
        default=env_value("IMAGE_RESPONSE_FORMAT") or None,
        help="Compatibility option for gateways that support response_format.",
    )
    parser.add_argument(
        "--base-url",
        default=env_value(*BASE_URL_ENV_NAMES),
        help="API base URL, with or without /v1.",
    )
    parser.add_argument(
        "--api-key",
        default=env_value(*API_KEY_ENV_NAMES),
        help="Bearer API key.",
    )
    parser.add_argument("--timeout", type=positive_int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--retries", type=positive_int, default=0)
    parser.add_argument("--retry-delay", type=float, default=2.0)
    return parser.parse_args(argv)


def validate_configuration(base_url: str, api_key: str) -> None:
    if not base_url:
        raise RuntimeError(
            "Missing GPT_IMAGE_2_BASE_URL. Set GPT_IMAGE_2_BASE_URL or pass --base-url."
        )
    if not api_key or api_key in {"<API_KEY>", "YOUR_API_KEY"}:
        raise RuntimeError(
            "Missing BASE_URL_API_KEY. Set BASE_URL_API_KEY or pass --api-key."
        )
    api_url(base_url, "generations")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validate_configuration(args.base_url, args.api_key)
    if args.mask and not args.images:
        raise RuntimeError("--mask requires at least one --image input.")

    payload = build_image_payload(
        model=args.model,
        prompt=args.prompt,
        size=args.size,
        quality=args.quality,
        output_format=args.output_format,
        output_compression=args.output_compression,
        moderation=args.moderation,
        response_format=args.response_format,
    )

    if args.images:
        body, content_type = build_edit_multipart(
            fields=payload,
            images=args.images,
            mask=args.mask,
            timeout=args.timeout,
        )
        response = request_multipart(
            url=api_url(args.base_url, "edits"),
            body=body,
            content_type=content_type,
            api_key=args.api_key,
            timeout=args.timeout,
            retries=args.retries,
            retry_delay=args.retry_delay,
        )
        operation = "edit"
    else:
        response = request_json(
            url=api_url(args.base_url, "generations"),
            payload=payload,
            api_key=args.api_key,
            timeout=args.timeout,
            retries=args.retries,
            retry_delay=args.retry_delay,
        )
        operation = "generate"

    image_bytes = extract_image_bytes(response, timeout=args.timeout)
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)

    print(
        json.dumps(
            {
                "operation": operation,
                "output": str(output_path),
                "size": args.size,
                "quality": args.quality,
                "output_format": args.output_format,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"generate_image.py: error: {exc}", file=sys.stderr)
        raise SystemExit(1)
