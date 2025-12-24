import requests

BACKEND_URL = "http://localhost:8000"


def summarize_article(url: str):
    resp = requests.post(f"{BACKEND_URL}/article/summarize", json={"url": url})
    return resp.json()
