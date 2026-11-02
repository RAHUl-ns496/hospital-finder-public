from datetime import datetime

from utils.mongo import get_database


DEFAULT_MEDICINES = [
    {"name": "Paracetamol 500mg", "category": "Fever and pain", "available": True, "quantity": 24, "prescription_required": False},
    {"name": "Cetirizine 10mg", "category": "Allergy relief", "available": True, "quantity": 18, "prescription_required": False},
    {"name": "ORS Sachets", "category": "Hydration", "available": True, "quantity": 40, "prescription_required": False},
    {"name": "Azithromycin 500mg", "category": "Antibiotic", "available": False, "quantity": 0, "prescription_required": True},
]


def get_pharmacy_record(name):
    return get_database()["pharmacies"].find_one({"name": name}, {"_id": 0}) or {}


def pharmacy_is_open(pharmacy):
    if pharmacy.get("open_24x7") or "24" in pharmacy.get("opening_hours", ""):
        return True, "Open 24×7"
    hours = pharmacy.get("opening_hours", "")
    if not hours or "-" not in hours:
        return None, hours or "Hours not listed"
    try:
        start, end = [part.strip() for part in hours.split("-", 1)]
        now = datetime.now().time()
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        is_open = start_time <= now <= end_time if start_time <= end_time else now >= start_time or now <= end_time
        return is_open, f"Open {hours}"
    except ValueError:
        return None, hours


def pharmacy_medicines(pharmacy):
    record = get_pharmacy_record(pharmacy.get("name", ""))
    medicines = record.get("medicines") or pharmacy.get("medicines") or DEFAULT_MEDICINES
    return medicines


def enrich_pharmacy(pharmacy):
    record = get_pharmacy_record(pharmacy.get("name", ""))
    merged = {**record, **pharmacy}
    if record.get("medicines"):
        merged["medicines"] = record["medicines"]
    open_now, status = pharmacy_is_open(merged)
    merged["open_now"] = open_now
    merged["open_status"] = status
    merged["medicines"] = pharmacy_medicines(merged)
    return merged
