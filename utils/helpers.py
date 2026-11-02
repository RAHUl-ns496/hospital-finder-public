import math
import re

EMERGENCY_NUMBERS = [
    ("🚑", "Ambulance",           "102"),
    ("🆘", "National Emergency",  "112"),
    ("👮", "Police",              "100"),
    ("🚒", "Fire Brigade",        "101"),
    ("🏥", "Medical Helpline",    "104"),
    ("☎️",  "Women Helpline",      "1091"),
    ("🧒", "Child Helpline",      "1098"),
    ("🩺", "AIIMS Delhi",         "011-26588500"),
    ("🧠", "Mental Health (iCall)","9152987821"),
    ("🩸", "Blood Bank",          "1910"),
    ("☠️",  "Poison Control",      "1800-116-117"),
    ("🛡️", "Disaster Mgmt",       "108"),
]

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

SPECIALITY_ICONS = {
    "emergency":    ("🚨 Emergency",    "b-red"),
    "icu":          ("🫀 ICU",          "b-red"),
    "trauma":       ("🩹 Trauma",       "b-red"),
    "cardiology":   ("❤️ Cardiology",   "b-blue"),
    "paediatrics":  ("🧒 Paediatrics",  "b-blue"),
    "gynaecology":  ("🤱 Gynaecology",  "b-blue"),
    "neurology":    ("🧠 Neurology",    "b-blue"),
    "oncology":     ("💊 Oncology",     "b-purple"),
    "radiology":    ("🔬 Radiology",    "b-green"),
    "surgery":      ("🔪 Surgery",      "b-orange"),
    "orthopaedics": ("🦴 Orthopaedics", "b-orange"),
    "dermatology":  ("🧴 Dermatology",  "b-blue"),
    "urology":      ("🫘 Urology",      "b-blue"),
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(2 * R * math.asin(math.sqrt(a)), 2)

def valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value.strip()))

def valid_phone(value):
    digits = re.sub(r"\D", "", value or "")
    return not value.strip() or 7 <= len(digits) <= 15

def directions_url(dlat, dlng, olat=None, olng=None):
    if olat and olng:
        return f"https://www.google.com/maps/dir/{olat},{olng}/{dlat},{dlng}"
    return f"https://www.google.com/maps/search/?api=1&query={dlat},{dlng}"

def gmaps_url(lat, lng):
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

def badge(text, cls="b-blue"):
    return f"<span class='badge {cls}'>{text}</span>"

def type_meta(ftype):
    m = {
        "hospital": ("Hospital",  "b-blue", "hosp"),
        "clinic":   ("Clinic",    "b-orange","clin"),
        "doctors":  ("Clinic",    "b-orange","clin"),
        "pharmacy": ("Pharmacy",  "b-green", "pharm"),
        "blood_donation_center": ("Blood Bank","b-red","blood"),
    }
    return m.get(ftype, (ftype.capitalize(),"b-blue","hosp"))

def sidebar_enum(items):
    html = ""
    for lbl, num in items:
        html += (f"<div class='enum-item'>"
                 f"<span class='lbl'>{lbl}</span>"
                 f"<span class='num'>{num}</span></div>")
    return html
