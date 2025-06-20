# scraper/utils.py

import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/113.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: Status {response.status_code}")

    return BeautifulSoup(response.text, "lxml")
