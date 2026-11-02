import streamlit as st
import random
import pandas as pd
from streamlit_folium import st_folium
from utils.styles import COMMON_CSS
from utils.helpers import EMERGENCY_NUMBERS, BLOOD_TYPES, directions_url
from utils.api import fetch_blood_banks, detect_ip_location, geocode_address
from utils.maps import build_blood_map
from utils.auth import check_auth

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["patient"])

for k,v in {"user_lat":None,"user_lng":None,"location_name":"",
            "blood_banks":[],"bb_searched":False,"bb_radius":15}.items():
    if k not in st.session_state: st.session_state[k]=v

def random_availability():
    return {bt: random.choice([0,0,random.randint(1,50),random.randint(1,30)]) for bt in BLOOD_TYPES}

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">🩸</div>
  <div><h1>Blood Bank Finder</h1>
       <p>Locate nearby blood banks · Check type availability · Get directions fast</p></div>
</div>""",unsafe_allow_html=True)
st.markdown("<div class='sos-banner'>🩸 Blood Bank Helpline: <b>1910</b> &nbsp;│&nbsp; Emergency: <b>112</b></div>",
            unsafe_allow_html=True)

with st.expander("📋 Blood Type Compatibility Chart"):
    c1,c2=st.columns(2)
    c1.markdown("""| Type | Donates To | Receives From |
|------|-----------|--------------|
| O- | Everyone | O- |
| O+ | O+,A+,B+,AB+ | O+,O- |
| A- | A-,A+,AB-,AB+ | A-,O- |
| A+ | A+,AB+ | A+,A-,O+,O- |""")
    c2.markdown("""| Type | Donates To | Receives From |
|------|-----------|--------------|
| B- | B-,B+,AB-,AB+ | B-,O- |
| B+ | B+,AB+ | B+,B-,O+,O- |
| AB- | AB-,AB+ | AB-,A-,B-,O- |
| AB+ | AB+ | Everyone |""")


# ── Search & Filters (Moved from Sidebar) ────
with st.expander("🔍 Search & Location Settings", expanded=not st.session_state.get('bb_searched', False)):

    st.markdown("<p class='sb-section'>📍 Location</p>",unsafe_allow_html=True)
    mode=st.radio("M",["🌐 Auto-detect","🔎 City","📌 Coords"],label_visibility="collapsed")
    if mode=="🌐 Auto-detect":
        if st.button("📡 Detect",use_container_width=True):
            with st.spinner("…"): lat,lng,city=detect_ip_location()
            if lat:
                st.session_state.user_lat=lat;st.session_state.user_lng=lng
                st.session_state.location_name=city;st.success(f"✅ {city}")
    elif mode=="🔎 City":
        addr=st.text_input("City",placeholder="e.g. Hyderabad")
        if st.button("🔍",use_container_width=True) and addr.strip():
            with st.spinner("…"): lat,lng,full=geocode_address(addr.strip())
            if lat:
                st.session_state.user_lat=lat;st.session_state.user_lng=lng
                st.session_state.location_name=full[:50]
    else:
        clat=st.number_input("Lat",value=28.6139,format="%.6f")
        clng=st.number_input("Lng",value=77.2090,format="%.6f")
        if st.button("📌 Set",use_container_width=True):
            st.session_state.user_lat=clat;st.session_state.user_lng=clng
            st.session_state.location_name=f"{clat:.4f},{clng:.4f}"
    if st.session_state.location_name: st.caption(f"📍 {st.session_state.location_name}")
    st.markdown("<hr>",unsafe_allow_html=True)
    radius=st.slider("Radius (km)",1,50,15)
    blood_filter=st.multiselect("Need Blood Type",BLOOD_TYPES)
    st.markdown("<hr>",unsafe_allow_html=True)
    no_loc=st.session_state.user_lat is None
    if no_loc: st.caption("⚠️ Set location first.")
    if st.button("🩸 Find Blood Banks",use_container_width=True,type="primary",disabled=no_loc):
        with st.spinner("Searching…"):
            result=fetch_blood_banks(st.session_state.user_lat,st.session_state.user_lng,radius)
        if result=="TIMEOUT": st.error("⏱️ Timeout.")
        else:
            for r in result: r["availability"]=random_availability()
            if blood_filter:
                result=[r for r in result if any(r["availability"].get(bt,0)>0 for bt in blood_filter)]
            st.session_state.blood_banks=result
            st.session_state.bb_radius=radius
            st.session_state.bb_searched=True; st.rerun()
    st.markdown("<hr>",unsafe_allow_html=True)
    for icon,lbl,num in EMERGENCY_NUMBERS[:4]:
        st.markdown(f"<div class='enum-item'><span class='lbl'>{icon} {lbl}</span>"
                    f"<span class='num'>{num}</span></div>",unsafe_allow_html=True)


if not st.session_state.bb_searched:
    st.info("👈 Set your location and click **Find Blood Banks**."); st.stop()

banks=st.session_state.blood_banks
m1,m2,m3=st.columns(3)
m1.metric("🩸 Found",  len(banks))
m2.metric("📍 Nearest",f"{banks[0]['distance_km']} km" if banks else "—")
m3.metric("🔍 Radius", f"{st.session_state.bb_radius} km")
st.caption("⚠️ Blood availability is simulated for demo. Always call ahead to confirm.")
st.markdown("---")
if not banks: st.warning("No blood banks found. Increase radius."); st.stop()

tab_map,tab_list=st.tabs(["🗺️ Map","📋 List"])
with tab_map:
    st_folium(build_blood_map(banks,st.session_state.user_lat,st.session_state.user_lng),
              use_container_width=True,height=480)
with tab_list:
    for b in banks:
        avail=b.get("availability",{})
        avail_html="".join(
            f"<span class='badge {'b-green' if u>0 else 'b-red'}'>{bt}: {'✅ '+str(u)+' u' if u>0 else '❌ Out'}</span>"
            for bt,u in avail.items())
        dir_url=directions_url(b["lat"],b["lng"],st.session_state.user_lat,st.session_state.user_lng)
        st.markdown(f"""
        <div class="h-card blood">
          <div style="display:flex;justify-content:space-between;flex-wrap:wrap;">
            <p class="h-name">🩸 {b["name"]}</p>
            <span class="badge b-dist">📍 {b["distance_km"]} km</span>
          </div>
          <p class="h-detail">📋 {b["address"]}</p>
          {"<p class='h-detail'>📞 "+b["phone"]+"</p>" if b["phone"] else ""}
          <div style="margin-top:8px;">{avail_html}</div>
          <div style="margin-top:10px;">
            <a class="action-btn btn-dir" href="{dir_url}" target="_blank">🗺️ Directions</a>
            {"<a class='action-btn btn-call' href='tel:"+b["phone"]+"'>📞 Call</a>" if b["phone"] else ""}
          </div>
        </div>""",unsafe_allow_html=True)
