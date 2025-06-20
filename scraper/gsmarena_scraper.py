# scraper/gsmarena_scraper.py

import re
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

    # Updated selector - GSMArena uses different structure
    phone_list = soup.select("div.makers ul li a")

    if not phone_list:
        # Try alternative selector
        phone_list = soup.select(".section-body ul li a")

    print(f"Found {len(phone_list)} phone links")

    for a in phone_list[:limit]:
        relative_url = a.get("href")
        if relative_url:
            # Handle both relative and absolute URLs
            if relative_url.startswith("http"):
                full_url = relative_url
            else:
                full_url = BASE_URL + relative_url.lstrip("/")
            phone_links.append(full_url)

    return phone_links


def scrape_phone_details(url: str) -> dict:
    """
    Scrapes the full specifications and metadata of a Samsung phone from GSMArena.
    Returns a dict with structured fields and a specs dict.
    """
    print(f"Scraping: {url}")
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

    # Get name - try multiple selectors
    title_elem = soup.find("h1", {"class": "specs-phone-name-title"})
    if not title_elem:
        title_elem = soup.find("h1")
    if not title_elem:
        title_elem = soup.select_one(".specs-brief-accent")

    if title_elem:
        phone_data["name"] = title_elem.get_text(strip=True)
        print(f"Found phone name: {phone_data['name']}")

    # Get image - try multiple selectors
    image_elem = soup.select_one(".specs-photo-main img")
    if not image_elem:
        image_elem = soup.select_one(".specs-photo img")
    if not image_elem:
        image_elem = soup.select_one("img.specs-photo")

    if image_elem and image_elem.get("src"):
        phone_data["image"] = image_elem["src"]

    # Go through spec table blocks
    spec_table = soup.find("div", {"id": "specs-list"})
    if not spec_table:
        spec_table = soup.find("table", {"cellspacing": "0"})

    if spec_table:
        print("Found spec table, processing...")

        # Handle different table structures
        tables = spec_table.select("table")
        if not tables:
            tables = [spec_table]  # The element itself might be a table

        for table in tables:
            # Get category from table header
            category_elem = table.find("th", {"class": "ttl"})
            if not category_elem:
                category_elem = table.find("th")

            category = "General"
            if category_elem:
                category = category_elem.get_text(strip=True)
                print(f"Processing category: {category}")

            # Process rows
            rows = table.select("tr")
            for row in rows:
                # Skip header rows
                if row.find("th", {"class": "ttl"}):
                    continue

                # Look for spec rows with ttl and nfo classes
                key_elem = row.find("td", {"class": "ttl"})
                value_elem = row.find("td", {"class": "nfo"})

                if not key_elem or not value_elem:
                    # Try alternative structure
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        key_elem = cells[0]
                        value_elem = cells[1]

                if key_elem and value_elem:
                    key = key_elem.get_text(strip=True)
                    value = value_elem.get_text(" ", strip=True)

                    if (
                        key and value and key != value
                    ):  # Avoid empty or duplicate entries
                        # Store in master spec dict
                        spec_key = f"{category} - {key}"
                        phone_data["specifications"][spec_key] = value
                        print(f"  {key}: {value}")

                        # Structured mapping with improved logic
                        key_lower = key.lower()
                        val_lower = value.lower()

                        # Release date mapping
                        if not phone_data["release_date"] and any(
                            term in key_lower
                            for term in ["announced", "release", "status"]
                        ):
                            phone_data["release_date"] = value

                        # Display size mapping
                        elif (
                            not phone_data["display_size"]
                            and "size" in key_lower
                            and any(
                                term in val_lower for term in ["inch", '"', "diagonal"]
                            )
                        ):
                            phone_data["display_size"] = value

                        # Resolution mapping
                        elif not phone_data["resolution"] and "resolution" in key_lower:
                            phone_data["resolution"] = value

                        # OS mapping
                        elif not phone_data["os"] and (
                            "os" in key_lower
                            or any(
                                term in val_lower
                                for term in ["android", "ios", "windows"]
                            )
                        ):
                            phone_data["os"] = value

                        # Chipset mapping
                        elif not phone_data["chipset"] and (
                            "chipset" in key_lower
                            or "cpu" in key_lower
                            or "processor" in key_lower
                        ):
                            phone_data["chipset"] = value

                        # Memory/RAM mapping - improved logic
                        elif (
                            "memory" in category.lower()
                            or "memory" in key_lower
                            or "ram" in key_lower
                            or "storage" in key_lower
                        ):

                            # RAM detection
                            if not phone_data["ram"] and (
                                "ram" in key_lower or "ram" in val_lower
                            ):
                                phone_data["ram"] = value
                            elif not phone_data["ram"] and re.search(
                                r"\d+\s*gb.*ram", val_lower
                            ):
                                # Extract RAM amount from value like "12GB RAM, 512GB storage"
                                ram_match = re.search(r"(\d+)\s*gb.*?ram", val_lower)
                                if ram_match:
                                    phone_data["ram"] = f"{ram_match.group(1)}GB"

                            # Storage detection
                            if not phone_data["storage"] and (
                                "internal" in key_lower
                                or "storage" in key_lower
                                or ("memory" in key_lower and "gb" in val_lower)
                            ):
                                phone_data["storage"] = value

                        # Camera mapping - improved detection
                        elif not phone_data["camera_main"] and (
                            (
                                "main camera" in category.lower()
                                or "primary camera" in category.lower()
                            )
                            or (
                                "camera" in key_lower
                                and any(
                                    term in val_lower
                                    for term in ["mp", "megapixel", "pixel"]
                                )
                            )
                        ):
                            phone_data["camera_main"] = value

                        # Battery mapping
                        elif not phone_data["battery"] and (
                            "battery" in category.lower()
                            or "battery" in key_lower
                            or "mah" in val_lower
                        ):
                            phone_data["battery"] = value

                        # Dimensions mapping
                        elif not phone_data["dimensions"] and "dimensions" in key_lower:
                            phone_data["dimensions"] = value

                        # Weight mapping
                        elif not phone_data["weight"] and "weight" in key_lower:
                            phone_data["weight"] = value

                        # Network mapping
                        elif not phone_data["network"] and (
                            "network" in category.lower() and "technology" in key_lower
                        ):
                            phone_data["network"] = value

    else:
        print("❌ No spec table found!")

    # Debug output
    print(f"Extracted structured data:")
    for key, value in phone_data.items():
        if key != "specifications" and value:
            print(f"  {key}: {value}")

    return phone_data


def save_phone_to_db(phone_data: dict, db):
    if not phone_data.get("name"):
        print("⚠️ Skipping phone with no name")
        return

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

    try:
        db.add(phone)
        db.commit()
        db.refresh(phone)  # Load phone.id

        # Add specifications
        specs = []
        for key, value in phone_data["specifications"].items():
            spec = Specification(phone_id=phone.id, key=key, value=value)
            specs.append(spec)

        if specs:
            db.add_all(specs)
            db.commit()

        print(f"✅ Saved to DB: {phone.name} with {len(specs)} specifications")

    except Exception as e:
        print(f"❌ Error saving {phone_data['name']}: {str(e)}")
        db.rollback()


def debug_page_structure(url: str):
    """
    Debug function to inspect the HTML structure of a phone page
    """
    soup = fetch_html(url)

    print(f"=== DEBUG: {url} ===")

    # Check for different title structures
    titles = [
        soup.find("h1", {"class": "specs-phone-name-title"}),
        soup.find("h1"),
        soup.select_one(".specs-brief-accent"),
    ]

    print("Title elements found:")
    for i, title in enumerate(titles):
        if title:
            print(f"  {i}: {title.get_text(strip=True)}")

    # Check for spec tables
    spec_containers = [
        soup.find("div", {"id": "specs-list"}),
        soup.find("table", {"cellspacing": "0"}),
        soup.select("table"),
    ]

    print("Spec containers found:")
    for i, container in enumerate(spec_containers):
        if container:
            if isinstance(container, list):
                print(f"  {i}: List with {len(container)} tables")
            else:
                print(
                    f"  {i}: {container.name} with id/class: {container.get('id', '')} {container.get('class', '')}"
                )


# 🧪 Test run
if __name__ == "__main__":
    db = SessionLocal()

    try:
        links = get_phone_links(limit=5)  # Start with fewer links for testing

        if not links:
            print("❌ No phone links found!")
        else:
            # Debug first URL structure
            print("=== DEBUGGING FIRST URL ===")
            debug_page_structure(links[0])
            print("=" * 50)

            for i, url in enumerate(links, 1):
                print(f"\n🔗 {i}/{len(links)}. Scraping: {url}")
                try:
                    phone_data = scrape_phone_details(url)
                    save_phone_to_db(phone_data, db)
                except Exception as e:
                    print(f"❌ Error processing {url}: {str(e)}")
                    continue

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
    finally:
        db.close()
