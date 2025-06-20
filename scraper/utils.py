# scraper/utils.py

import requests
from bs4 import BeautifulSoup
import time
import random


def fetch_html(url: str, delay: bool = True) -> BeautifulSoup:
    """
    Fetch HTML content with better headers and optional delay to avoid being blocked
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # Add random delay to avoid being blocked
    if delay:
        time.sleep(random.uniform(1, 3))

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        return BeautifulSoup(response.text, "lxml")

    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {str(e)}")
        raise Exception(f"Failed to fetch {url}: {str(e)}")
