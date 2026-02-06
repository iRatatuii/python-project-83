from bs4 import BeautifulSoup


def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.h1.string if soup.h1 else ""
    title = soup.title.string if soup.title else ""

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag["content"] if description_tag else ""
    return title, h1, description
