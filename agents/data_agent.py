# agents/data_agent.py

from sqlalchemy.orm import Session
from config.database import SessionLocal
from database.models import Phone, Specification


def get_phone_data(phone_name: str) -> dict:
    """
    Fetch phone data and specs by name from the database.
    Returns a dict with all structured fields + specs.
    """
    db: Session = SessionLocal()
    phone = db.query(Phone).filter(Phone.name.ilike(f"%{phone_name}%")).first()

    if not phone:
        return {"error": f"No phone found with name matching: {phone_name}"}

    specs = db.query(Specification).filter(Specification.phone_id == phone.id).all()

    structured = {
        "Name": phone.name,
        "Battery": phone.battery,
        "Camera": phone.camera_main,
        "Display": phone.display_size,
        "Chipset": phone.chipset,
        "OS": phone.os,
        "RAM": phone.ram,
        "Storage": phone.storage,
        "Release Date": phone.release_date,
        "Network": phone.network,
        "Dimensions": phone.dimensions,
        "Weight": phone.weight,
    }

    extra_specs = {spec.key: spec.value for spec in specs}

    return {"structured": structured, "extra": extra_specs}


def format_phone_specs(data: dict) -> str:
    """
    Converts structured + extra specs into a formatted string.
    """
    if "error" in data:
        return data["error"]

    parts = [" Phone Specifications:\n"]
    for key, val in data["structured"].items():
        if val:
            parts.append(f"{key}: {val}")

    parts.append("\n Additional Specifications:\n")
    for key, val in data["extra"].items():
        parts.append(f"{key}: {val}")

    return "\n".join(parts)


"""
# Test run
if __name__ == "__main__":
    name = "Galaxy S23"
    data = get_phone_data(name)
    formatted = format_phone_specs(data)
    print(formatted)
"""
