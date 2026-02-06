import requests

from .parser import parse_html


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
