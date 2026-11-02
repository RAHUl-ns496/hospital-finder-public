import folium
from utils.helpers import directions_url

TILE = "CartoDB positron"

def _popup(h, ulat, ulng):
    ph = f"📞 {h['phone']}<br>" if h["phone"] else ""
    return folium.Popup(
        f"""<div style="min-width:200px;font-family:sans-serif;">
        <b style="font-size:14px;color:#1a237e;">{h["name"]}</b><br>
        <span style="font-size:12px;color:#555;">📍 {h["address"]}</span><br>
        {ph}<span style="font-size:12px;font-weight:700;color:#1565c0;">🚗 {h["distance_km"]} km</span><br><br>
        <a href="{directions_url(h["lat"],h["lng"],ulat,ulng)}" target="_blank"
           style="background:#1565c0;color:#fff;padding:5px 12px;border-radius:6px;
                  text-decoration:none;font-size:12px;">🗺️ Directions</a>
        </div>""",
        max_width=260
    )

def _user_marker(m, lat, lng):
    folium.Marker(
        [lat, lng], popup="📍 Your Location", tooltip="You are here",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(m)

def build_hospital_map(hospitals, ulat, ulng):
    m = folium.Map(location=[ulat, ulng], zoom_start=13, tiles=TILE)
    _user_marker(m, ulat, ulng)
    color_map = {"hospital":"red","clinic":"orange","doctors":"orange"}
    for h in hospitals:
        color = color_map.get(h["type"],"red")
        folium.Marker(
            [h["lat"], h["lng"]],
            popup=_popup(h, ulat, ulng),
            tooltip=f"🏥 {h['name']} ({h['distance_km']} km)",
            icon=folium.Icon(color=color, icon="plus-sign", prefix="glyphicon")
        ).add_to(m)
    return m

def build_pharmacy_map(pharmacies, ulat, ulng):
    m = folium.Map(location=[ulat, ulng], zoom_start=14, tiles=TILE)
    _user_marker(m, ulat, ulng)
    for p in pharmacies:
        folium.Marker(
            [p["lat"], p["lng"]],
            popup=_popup(p, ulat, ulng),
            tooltip=f"💊 {p['name']} ({p['distance_km']} km)",
            icon=folium.Icon(color="green", icon="plus-sign", prefix="glyphicon")
        ).add_to(m)
    return m

def build_blood_map(banks, ulat, ulng):
    m = folium.Map(location=[ulat, ulng], zoom_start=13, tiles=TILE)
    _user_marker(m, ulat, ulng)
    for b in banks:
        folium.Marker(
            [b["lat"], b["lng"]],
            popup=_popup(b, ulat, ulng),
            tooltip=f"🩸 {b['name']} ({b['distance_km']} km)",
            icon=folium.Icon(color="darkred", icon="tint", prefix="fa")
        ).add_to(m)
    return m

def build_single_route_map(hospital, ulat, ulng):
    mid_lat = (hospital["lat"] + ulat) / 2
    mid_lng = (hospital["lng"] + ulng) / 2
    m = folium.Map(location=[mid_lat, mid_lng], zoom_start=13, tiles=TILE)
    _user_marker(m, ulat, ulng)
    folium.Marker(
        [hospital["lat"], hospital["lng"]],
        popup=_popup(hospital, ulat, ulng),
        tooltip=f"🏥 {hospital['name']}",
        icon=folium.Icon(color="red", icon="plus-sign", prefix="glyphicon")
    ).add_to(m)
    folium.PolyLine(
        [[ulat, ulng], [hospital["lat"], hospital["lng"]]],
        color="#e53935", weight=3, opacity=0.7, dash_array="8"
    ).add_to(m)
    return m
