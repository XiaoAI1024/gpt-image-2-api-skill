#!/usr/bin/env python3
"""Check Python and API configuration for gpt-image-2-api-skill."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys


MIN_PYTHON = (3, 9)
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


def configuration_help() -> str:
    return """Required API configuration:

macOS/Linux:
  export GPT_IMAGE_2_BASE_URL="https://api.openai.com"
  export BASE_URL_API_KEY="YOUR_API_KEY"

Then test:
  python3 scripts/check_environment.py
"""


def is_configured(value: str, placeholders: set[str] | None = None) -> bool:
    if not value or not value.strip():
        return False
    if placeholders and value.strip() in placeholders:
        return False
    return True


def collect_status(base_url: str | None = None, api_key: str | None = None) -> dict:
    resolved_base_url = (
        base_url
        if base_url is not None
        else env_value(*BASE_URL_ENV_NAMES)
    )
    resolved_api_key = (
        api_key
        if api_key is not None
        else env_value(*API_KEY_ENV_NAMES)
    )
    python_ok = sys.version_info >= MIN_PYTHON
    base_url_configured = is_configured(resolved_base_url)
    api_key_configured = is_configured(
        resolved_api_key,
        placeholders={"<API_KEY>", "YOUR_API_KEY"},
    )

    return {
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "python_ok": python_ok,
        "python_minimum": ".".join(str(part) for part in MIN_PYTHON),
        "base_url_configured": base_url_configured,
        "api_key_configured": api_key_configured,
        "ready": python_ok and base_url_configured and api_key_configured,
    }


def print_text_report(status: dict) -> None:
    print("gpt-image-2-api-skill environment check")
    print(f"- Python: {status['python_version']} ({status['python_executable']})")
    print(f"- Python {status['python_minimum']}+: {'OK' if status['python_ok'] else 'MISSING'}")
    print(f"- GPT_IMAGE_2_BASE_URL configured: {'yes' if status['base_url_configured'] else 'no'}")
    print(f"- BASE_URL_API_KEY configured: {'yes' if status['api_key_configured'] else 'no'}")
    print(f"- Ready: {'yes' if status['ready'] else 'no'}")
    if not status["ready"]:
        print("")
        print(configuration_help())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Python version and API configuration."
    )
    parser.add_argument("--base-url", help="API base URL to check.")
    parser.add_argument("--api-key", help="API key to check.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    status = collect_status(base_url=args.base_url, api_key=args.api_key)
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print_text_report(status)
    return 0 if status["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
