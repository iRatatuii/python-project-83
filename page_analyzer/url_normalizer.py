from bs4 import BeautifulSoup
import requests


def analyze_url(url):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        h1 = soup.h1.string if soup.h1 else ""
        title = soup.title.string if soup.title else ""

        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else ""

        return {
            "status_code": resp.status_code,
            "h1": h1,
            "title": title,
            "description": description,
        }

    except requests.RequestException:
        return None
