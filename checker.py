"""
url-health-checker: check a list of URLs and report status, latency, and SSL info.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass

import requests
import urllib3
from urllib3.util import Retry
from requests.adapters import HTTPAdapter


@dataclass
class HealthResult:
    url: str
    status_code: int | None
    latency_ms: float | None
    error: str | None = None


def build_session(max_retries: int = 3) -> requests.Session:
    """Session with sane retry behavior for flaky endpoints."""
    session = requests.Session()
    retry = Retry(total=max_retries, backoff_factor=0.5, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def check_url(session: requests.Session, url: str, timeout: float = 5.0) -> HealthResult:
    start = time.monotonic()
    try:
        response = session.get(url, timeout=timeout)
        latency_ms = (time.monotonic() - start) * 1000
        return HealthResult(url=url, status_code=response.status_code, latency_ms=round(latency_ms, 1))
    except requests.RequestException as exc:
        return HealthResult(url=url, status_code=None, latency_ms=None, error=str(exc))


def check_urls(urls: list[str]) -> list[HealthResult]:
    session = build_session()
    return [check_url(session, url) for url in urls]


def print_report(results: list[HealthResult]) -> None:
    for result in results:
        if result.error:
            print(f"✗ {result.url} — ERROR: {result.error}")
        else:
            status_icon = "✓" if result.status_code and result.status_code < 400 else "✗"
            print(f"{status_icon} {result.url} — {result.status_code} ({result.latency_ms}ms)")


def main() -> None:
    urls = sys.argv[1:] or ["https://www.python.org", "https://github.com"]
    results = check_urls(urls)
    print_report(results)


if __name__ == "__main__":
    main()

def load_config(path: str) -> dict:
    """Load optional YAML config for target URLs."""
    import yaml
    with open(path) as f:
        return yaml.safe_load(f) or {}

def thumbnail_preview(image_path: str, size: tuple = (128, 128)):
    """Generate a small preview thumbnail for a downloaded asset."""
    from PIL import Image
    with Image.open(image_path) as img:
        img.thumbnail(size)
        return img
