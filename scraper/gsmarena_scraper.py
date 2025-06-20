# scraper/gsmarena_scraper.py

from scraper.utils import fetch_html
from bs4 import BeautifulSoup
from config.database import SessionLocal
from database.models import Phone, Specification

BASE_URL = "https://www.gsmarena.com/"
SAMSUNG_PHONE_LIST_URL = f"{BASE_URL}samsung-phones-9.php"


def get_phone_links(limit=15):
    """
    Scrapes the main Samsung phones list page and returns the full URLs of phone models.
    """
    soup = fetch_html(SAMSUNG_PHONE_LIST_URL)
    phone_links = []

    # Phone links are inside <div class="makers"> → <ul> → <li> → <a>
    phone_list = soup.select("div.makers ul li a")

    for a in phone_list[:limit]:
        relative_url = a["href"]
        full_url = BASE_URL + relative_url
        phone_links.append(full_url)

    return phone_links


def scrape_phone_details(url: str) -> dict:
    """
    Scrapes the full specifications and metadata of a Samsung phone from GSMArena.
    Returns a dict with structured fields and a specs dict.
    """
    soup = fetch_html(url)

    phone_data = {
        "url": url,
        "name": None,
        "image": None,
        "release_date": None,
        "display_size": None,
        "resolution": None,
        "os": None,
        "chipset": None,
        "ram": None,
        "storage": None,
        "camera_main": None,
        "battery": None,
        "network": None,
        "dimensions": None,
        "weight": None,
        "specifications": {},
    }

    # Get name
    title_elem = soup.find("h1", {"class": "specs-phone-name-title"})
    if title_elem:
        phone_data["name"] = title_elem.get_text(strip=True)

    # Get image
    image_elem = soup.select_one(".specs-photo-main img")
    if image_elem and image_elem.get("src"):
        phone_data["image"] = image_elem["src"]

    # Go through spec table blocks
    spec_table = soup.find("div", {"id": "specs-list"})
    if spec_table:
        for table in spec_table.select("table"):
            category = (
                table.find("th").get_text(strip=True) if table.find("th") else "General"
            )

            for row in table.select("tr"):
                if row.th and row.td:
                    key = row.th.get_text(strip=True)
                    value = row.td.get_text(" ", strip=True)

                    # Store in master spec dict
                    phone_data["specifications"][f"{category} - {key}"] = value

                    key_lower = key.lower()
                    val_lower = value.lower()

                    # Structured mapping
                    if not phone_data["release_date"] and (
                        "release" in key_lower or "announced" in key_lower
                    ):
                        phone_data["release_date"] = value

                    elif (
                        not phone_data["display_size"]
                        and category.lower() == "display"
                        and "size" in key_lower
                    ):
                        phone_data["display_size"] = value

                    elif not phone_data["resolution"] and "resolution" in key_lower:
                        phone_data["resolution"] = value

                    elif not phone_data["os"] and (
                        "os" in key_lower or "android" in val_lower
                    ):
                        phone_data["os"] = value

                    elif not phone_data["chipset"] and "chipset" in key_lower:
                        phone_data["chipset"] = value

                    elif category.lower() == "memory":
                        if not phone_data["ram"] and (
                            "ram" in val_lower or "gb" in val_lower
                        ):
                            match = re.search(r"\d+\s?gb", val_lower)
                            if match:
                                phone_data["ram"] = match.group(0)
                        if not phone_data["storage"] and "internal" in key_lower:
                            phone_data["storage"] = value

                    elif not phone_data["camera_main"] and category.lower().startswith(
                        "main camera"
                    ):
                        phone_data["camera_main"] = value

                    elif not phone_data["battery"] and (
                        "battery" in category.lower()
                        or "battery" in key_lower
                        or "mah" in val_lower
                    ):
                        phone_data["battery"] = value

                    elif not phone_data["dimensions"] and "dimensions" in key_lower:
                        phone_data["dimensions"] = value

                    elif not phone_data["weight"] and "weight" in key_lower:
                        phone_data["weight"] = value

                    elif (
                        not phone_data["network"]
                        and category.lower() == "network"
                        and "technology" in key_lower
                    ):
                        phone_data["network"] = value

    return phone_data


def save_phone_to_db(phone_data: dict, db):
    # Check if phone already exists
    existing = db.query(Phone).filter(Phone.name == phone_data["name"]).first()
    if existing:
        print(f"⚠️ Skipping {phone_data['name']} (already in DB)")
        return

    # Create Phone instance
    phone = Phone(
        name=phone_data["name"],
        url=phone_data["url"],
        image=phone_data["image"],
        release_date=phone_data["release_date"],
        display_size=phone_data["display_size"],
        resolution=phone_data["resolution"],
        os=phone_data["os"],
        chipset=phone_data["chipset"],
        ram=phone_data["ram"],
        storage=phone_data["storage"],
        camera_main=phone_data["camera_main"],
        battery=phone_data["battery"],
        network=phone_data["network"],
        dimensions=phone_data["dimensions"],
        weight=phone_data["weight"],
    )

    db.add(phone)
    db.commit()
    db.refresh(phone)  # Load phone.id

    # Add specifications
    specs = []
    for key, value in phone_data["specifications"].items():
        spec = Specification(phone_id=phone.id, key=key, value=value)
        specs.append(spec)

    db.add_all(specs)
    db.commit()

    print(f"✅ Saved to DB: {phone.name}")


# 🧪 Test run
if __name__ == "__main__":
    db = SessionLocal()

    links = get_phone_links()
    for i, url in enumerate(links, 1):
        print(f"\n🔗 {i}. Scraping: {url}")
        phone_data = scrape_phone_details(url)
        save_phone_to_db(phone_data, db)

    db.close()
