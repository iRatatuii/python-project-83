from urllib.parse import urlparse

import requests
import validators

from .parser import parse_html


def prepare_url(raw_url: str):
    data = raw_url.strip()
    if not data:
        return None, "URL не может быть пустым"

    normalize_url = urlparse(data)

    if not normalize_url.scheme or not normalize_url.hostname:
        return None, "Некорректный URL"

    url = f"{normalize_url.scheme}://{normalize_url.hostname}"

    if len(url) > 255:
        return None, "URL не может быть длиннее 255 символов"

    if not validators.url(url):
        return None, "Некорректный URL"

    return url, None


def analyze_url(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        html = resp.text

        title, h1, description = parse_html(html)

        return {
            "status_code": resp.status_code,
            "h1": h1,
            "title": title,
            "description": description,
        }

    except requests.RequestException:
        return None
