import streamlit as st
import requests
import geocoder
from geopy.geocoders import Nominatim
from utils.helpers import haversine

@st.cache_data(ttl=300, show_spinner=False)
def fetch_osm(lat, lng, radius_km, amenity_list):
    radius_m = int(radius_km * 1000)
    union = "\n".join([
        f'  node["{k}"="{v}"](around:{radius_m},{lat},{lng});'
        f'  way["{k}"="{v}"](around:{radius_m},{lat},{lng});'
        for k, v in amenity_list
    ])
    query = f"[out:json][timeout:35];\n(\n{union}\n);\nout center tags;"
    try:
        resp = requests.post("https://overpass-api.de/api/interpreter",
                             data={"data": query}, timeout=40)
        resp.raise_for_status()
        return resp.json().get("elements", [])
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception:
        return []

def parse_elements(elements, user_lat, user_lng, ftype_key="amenity"):
    results = []
    for el in (elements if isinstance(elements, list) else []):
        tags = el.get("tags", {})
        name = (tags.get("name") or tags.get("name:en") or "").strip()
        if not name:
            continue
        if el["type"] == "node":
            hlat, hlng = el["lat"], el["lon"]
        else:
            c = el.get("center", {})
            hlat, hlng = c.get("lat"), c.get("lon")
        if not hlat or not hlng:
            continue

        dist = haversine(user_lat, user_lng, hlat, hlng)
        addr_parts = [tags.get("addr:housenumber",""), tags.get("addr:street",""),
                      tags.get("addr:suburb",""), tags.get("addr:city",""),
                      tags.get("addr:state","")]
        address = ", ".join(p for p in addr_parts if p).strip(", ") \
                  or tags.get("addr:full","Address not listed")
        spec_raw = tags.get("healthcare:speciality", tags.get("speciality",""))
        specialities = [s.strip() for s in spec_raw.split(";") if s.strip()] if spec_raw else []

        results.append({
            "name": name, "lat": hlat, "lng": hlng, "distance_km": dist,
            "phone": tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or "",
            "website": tags.get("website") or tags.get("contact:website") or "",
            "address": address,
            "type": tags.get(ftype_key) or tags.get("healthcare") or tags.get("amenity") or "hospital",
            "emergency": tags.get("emergency",""),
            "beds": tags.get("beds",""),
            "opening_hours": tags.get("opening_hours",""),
            "operator": tags.get("operator",""),
            "wheelchair": tags.get("wheelchair",""),
            "specialities": specialities,
        })
    return sorted(results, key=lambda x: x["distance_km"])

def fetch_hospitals(lat, lng, radius_km):
    elements = fetch_osm(lat, lng, radius_km, [
        ("amenity","hospital"), ("amenity","clinic"),
        ("healthcare","hospital"),
    ])
    
    results = []
    if elements != "TIMEOUT":
        results = parse_elements(elements, lat, lng)
        
    # If OSM fails, returns empty, or times out, provide rich mock data so the UI can be tested
    if not results or elements == "TIMEOUT":
        import random
        results = [
            {
                "name": f"City Care Hospital (Mock)", "lat": lat + 0.01, "lng": lng + 0.01, "distance_km": 1.2,
                "phone": "+91 98765 43210", "website": "https://example.com", "address": "123 Main Street",
                "type": "hospital", "emergency": "yes", "beds": "250", "opening_hours": "24/7",
                "operator": "City Care Group", "wheelchair": "yes", "specialities": ["Cardiology", "Neurology"]
            },
            {
                "name": f"Sunrise Clinic (Mock)", "lat": lat - 0.015, "lng": lng + 0.005, "distance_km": 2.5,
                "phone": "+91 11223 34455", "website": "", "address": "45 West Avenue",
                "type": "clinic", "emergency": "no", "beds": "15", "opening_hours": "09:00-21:00",
                "operator": "Sunrise Health", "wheelchair": "limited", "specialities": ["Pediatrics", "General"]
            },
            {
                "name": f"Metro General Hospital (Mock)", "lat": lat + 0.02, "lng": lng - 0.02, "distance_km": 3.8,
                "phone": "+91 99887 76655", "website": "https://metrohospital.com", "address": "88 North Road",
                "type": "hospital", "emergency": "yes", "beds": "500", "opening_hours": "24/7",
                "operator": "Metro Health", "wheelchair": "yes", "specialities": ["Trauma", "Orthopedics"]
            }
        ]
        
    return results

def fetch_blood_banks(lat, lng, radius_km):
    elements = fetch_osm(lat, lng, radius_km, [
        ("amenity", "blood_bank"), ("healthcare", "blood_bank")
    ])
    
    results = []
    if elements != "TIMEOUT":
        results = parse_elements(elements, lat, lng)
        
    if not results or elements == "TIMEOUT":
        results = [
            {"name": "Red Cross Blood Bank (Mock)", "lat": lat+0.015, "lng": lng-0.01, "distance_km": 1.8, "phone": "1910", "address": "Central District", "type": "blood_bank"},
            {"name": "City Lifeline Blood Center (Mock)", "lat": lat-0.02, "lng": lng+0.02, "distance_km": 3.1, "phone": "+91 88888 88888", "address": "East Block", "type": "blood_bank"}
        ]
    return results

def fetch_pharmacies(lat, lng, radius_km):
    elements = fetch_osm(lat, lng, radius_km, [
        ("amenity", "pharmacy"), ("healthcare", "pharmacy")
    ])
    
    results = []
    if elements != "TIMEOUT":
        results = parse_elements(elements, lat, lng)
        
    if not results or elements == "TIMEOUT":
        results = [
            {"name": "Apollo Pharmacy 24x7 (Mock)", "lat": lat+0.005, "lng": lng+0.005, "distance_km": 0.8, "phone": "+91 99999 11111", "address": "Market Road", "type": "pharmacy", "opening_hours": "24/7"},
            {"name": "Wellness Chemist (Mock)", "lat": lat-0.01, "lng": lng-0.01, "distance_km": 1.5, "phone": "+91 77777 22222", "address": "South Avenue", "type": "pharmacy", "opening_hours": "08:00-22:00"},
            {"name": "MedPlus (Mock)", "lat": lat+0.02, "lng": lng-0.005, "distance_km": 2.2, "phone": "+91 55555 33333", "address": "North Square", "type": "pharmacy", "opening_hours": "24/7"}
        ]
    return results

@st.cache_data(ttl=600, show_spinner=False)
def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="emerg_hospital_finder_v3")
        loc = geolocator.geocode(address, timeout=10)
        if loc:
            return loc.latitude, loc.longitude, loc.address
        return None, None, None
    except Exception:
        return None, None, None

def detect_ip_location():
    try:
        g = geocoder.ip("me")
        if g.latlng:
            return g.latlng[0], g.latlng[1], g.city or "Your Location"
        return None, None, None
    except Exception:
        return None, None, None
