import requests


def fetch_article_text(url: str) -> str:
    """Placeholder: fetch article HTML and extract text."""
    try:
        r = requests.get(url, timeout=10)
        return r.text
    except Exception:
        return ""
