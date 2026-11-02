import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from utils.styles import COMMON_CSS
from utils.helpers import EMERGENCY_NUMBERS, SPECIALITY_ICONS, directions_url, type_meta
from utils.api import fetch_hospitals, geocode_address, detect_ip_location
from utils.maps import build_hospital_map, build_single_route_map
from utils.auth import update_user_fields
from utils.auth import check_auth

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["patient"])

for k,v in {"user_lat":None,"user_lng":None,"location_name":"",
            "hospitals":[],"h_searched":False,"h_radius":10,"saved_hospitals":[]}.items():
    if k not in st.session_state: st.session_state[k]=v


# ── Header ────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">🏥</div>
  <div><h1>Find Nearby Hospitals</h1>
       <p>Live OSM data · Map view · Directions · One-click call</p></div>
</div>""",unsafe_allow_html=True)
st.markdown("<div class='sos-banner'>⚠️ Emergency? Call 112 | Ambulance: 102 | Police: 100</div>",
            unsafe_allow_html=True)


# ── Search & Filters (Moved from Sidebar) ────
with st.expander("🔍 Search & Location Settings", expanded=not st.session_state.get('h_searched', False)):

    st.markdown("<p class='sb-section'>📍 Location</p>", unsafe_allow_html=True)
    mode=st.radio("M",["🌐 Auto-detect","🔎 City","📌 Coords"],label_visibility="collapsed")
    if mode=="🌐 Auto-detect":
        if st.button("📡 Detect",use_container_width=True):
            with st.spinner("Detecting…"): lat,lng,city=detect_ip_location()
            if lat:
                st.session_state.user_lat=lat; st.session_state.user_lng=lng
                st.session_state.location_name=city; st.success(f"✅ {city}")
            else: st.error("Failed.")
    elif mode=="🔎 City":
        addr=st.text_input("City/Address",placeholder="e.g. Bandra, Mumbai")
        if st.button("🔍 Search",use_container_width=True) and addr.strip():
            with st.spinner("…"): lat,lng,full=geocode_address(addr.strip())
            if lat:
                st.session_state.user_lat=lat; st.session_state.user_lng=lng
                st.session_state.location_name=full[:55]; st.success("✅")
            else: st.error("Not found.")
    else:
        clat=st.number_input("Lat",value=28.6139,format="%.6f")
        clng=st.number_input("Lng",value=77.2090,format="%.6f")
        if st.button("📌 Set",use_container_width=True):
            st.session_state.user_lat=clat; st.session_state.user_lng=clng
            st.session_state.location_name=f"{clat:.4f},{clng:.4f}"; st.success("✅")
    if st.session_state.location_name:
        st.caption(f"📍 {st.session_state.location_name}")
    st.markdown("<hr>",unsafe_allow_html=True)
    st.markdown("<p class='sb-section'>⚙️ Filters</p>",unsafe_allow_html=True)
    radius=st.slider("Radius (km)",1,50,10)
    show_types=st.multiselect("Types",["Hospital","Clinic"],default=["Hospital","Clinic"])
    sort_by=st.selectbox("Sort",["📍 Distance","🔤 Name"])
    st.markdown("<hr>",unsafe_allow_html=True)
    no_loc=st.session_state.user_lat is None
    if no_loc: st.caption("⚠️ Set location first.")
    if st.button("🔍 Find Hospitals",use_container_width=True,type="primary",disabled=no_loc):
        with st.spinner("Fetching from OpenStreetMap…"):
            result=fetch_hospitals(st.session_state.user_lat,st.session_state.user_lng,radius)
        if result=="TIMEOUT": st.error("⏱️ Timeout. Try smaller radius.")
        else:
            type_map=[]
            if "Hospital" in show_types: type_map+=["hospital"]
            if "Clinic"   in show_types: type_map+=["clinic","doctors"]
            filtered=[h for h in result if h["type"] in type_map] if type_map else result
            if "Name" in sort_by: filtered.sort(key=lambda x:x["name"].lower())
            st.session_state.hospitals=filtered
            st.session_state.h_radius=radius
            st.session_state.h_searched=True
            st.rerun()
    st.markdown("<hr>",unsafe_allow_html=True)
    for icon,lbl,num in EMERGENCY_NUMBERS[:5]:
        st.markdown(f"<div class='enum-item'><span class='lbl'>{icon} {lbl}</span>"
                    f"<span class='num'>{num}</span></div>",unsafe_allow_html=True)

if not st.session_state.h_searched:
    c1,c2,c3,c4=st.columns(4)
    for col,(icon,ttl,desc) in zip([c1,c2,c3,c4],[
        ("📍","Set Location","Auto-detect, search city, or enter coords"),
        ("⚙️","Apply Filters","Radius 1–50 km, hospital/clinic filter"),
        ("🏥","Find Hospitals","Real OSM data, no API key needed"),
        ("🗺️","Get Directions","One-click Google Maps navigation"),
    ]):
        with col:
            st.markdown(f"<div class='welcome-card'><div class='icon'>{icon}</div>"
                        f"<h4>{ttl}</h4><p>{desc}</p></div>",unsafe_allow_html=True)
    st.info("👈 Set your location and click **Find Hospitals**.")
    st.stop()

hospitals=st.session_state.hospitals
m1,m2,m3,m4=st.columns(4)
m1.metric("🏥 Found",         len(hospitals))
m2.metric("📍 Nearest",       f"{hospitals[0]['distance_km']} km" if hospitals else "—")
m3.metric("📞 Have Phone",    sum(1 for h in hospitals if h["phone"]))
m4.metric("🔍 Radius",        f"{st.session_state.h_radius} km")
st.markdown("---")
if not hospitals: st.warning("No hospitals found. Try larger radius."); st.stop()

tab_map,tab_list,tab_table=st.tabs(["🗺️ Map","📋 List","📊 Table + CSV"])

with tab_map:
    flt=st.text_input("🔎 Filter",placeholder="Hospital name…",key="mapflt")
    disp=[h for h in hospitals if flt.lower() in h["name"].lower()] if flt else hospitals
    st_folium(build_hospital_map(disp,st.session_state.user_lat,st.session_state.user_lng),
              use_container_width=True,height=520)
    st.caption("🔵 You · 🔴 Hospital · 🟠 Clinic")

with tab_list:
    sq=st.text_input("🔎 Filter",placeholder="e.g. Apollo, AIIMS…",key="listflt")
    disp=[h for h in hospitals if sq.lower() in h["name"].lower()] if sq else hospitals
    for h in disp:
        type_lbl,type_badge,card_cls=type_meta(h["type"])
        dir_url=directions_url(h["lat"],h["lng"],st.session_state.user_lat,st.session_state.user_lng)
        cc,ca=st.columns([5,1])
        with cc:
            ph_html   = f"<p class='h-detail'>📞 {h['phone']}</p>" if h["phone"] else ""
            oh_html   = f"<span class='badge b-green'>🕐 {h['opening_hours']}</span>" if h["opening_hours"] else ""
            beds_html = f"<span class='badge b-blue'>🛏️ {h['beds']}</span>" if h["beds"] else ""
            st.markdown(f"""
            <div class="h-card {card_cls}">
              <div style="display:flex;justify-content:space-between;flex-wrap:wrap;">
                <p class="h-name">🏥 {h["name"]}</p>
                <span class="badge b-dist">📍 {h["distance_km"]} km</span>
              </div>
              <p class="h-detail">📋 {h["address"]}</p>{ph_html}
              <div style="margin-top:6px;">
                <span class="badge {type_badge}">{type_lbl}</span>{oh_html}{beds_html}
              </div>
            </div>""",unsafe_allow_html=True)
        with ca:
            st.markdown(f"""<div style="padding-top:10px;display:flex;flex-direction:column;gap:6px;">
              <a class="action-btn btn-dir" href="{dir_url}" target="_blank">🗺️ Directions</a>
              {"<a class='action-btn btn-call' href='tel:"+h['phone']+"'>📞 Call</a>" if h["phone"] else ""}
            </div>""",unsafe_allow_html=True)
            if st.button("💾",key=f"sv_{h['name'][:15]}",help="Save"):
                saved=st.session_state.saved_hospitals
                if not any(s["name"]==h["name"] for s in saved):
                    saved.append(h)
                    update_user_fields(st.session_state.user_email, {"saved_hospitals": saved})
                    st.success("Saved!")
        with st.expander(f"🗺️ Route to {h['name'][:35]}"):
            st_folium(build_single_route_map(h,st.session_state.user_lat,st.session_state.user_lng),
                      use_container_width=True,height=280,key=f"r_{h['lat']}_{h['lng']}")

with tab_table:
    df=pd.DataFrame([{"Name":h["name"],"Type":h["type"].capitalize(),
        "Distance (km)":h["distance_km"],"Phone":h["phone"] or "—",
        "Address":h["address"],"Opening Hours":h["opening_hours"] or "—"} for h in hospitals])
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download CSV",df.to_csv(index=False),"hospitals.csv","text/csv")
