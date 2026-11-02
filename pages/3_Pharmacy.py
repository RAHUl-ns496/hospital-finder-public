import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from utils.styles import COMMON_CSS
from utils.helpers import EMERGENCY_NUMBERS, directions_url
from utils.auth import check_auth
from utils.api import fetch_pharmacies, detect_ip_location, geocode_address
from utils.maps import build_pharmacy_map
from utils.pharmacy import enrich_pharmacy

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["patient"])

for k,v in {"user_lat":None,"user_lng":None,"location_name":"",
            "pharmacies":[],"ph_searched":False,"ph_radius":5}.items():
    if k not in st.session_state: st.session_state[k]=v

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">💊</div>
  <div><h1>24×7 Pharmacy Finder</h1>
       <p>Find open pharmacies near you · Night chemist locator · Get medicines fast</p></div>
</div>""",unsafe_allow_html=True)
st.markdown("<div class='sos-banner'>💊 Pharmacy Helpline: <b>1800-180-1104</b> &nbsp;│&nbsp; Emergency: <b>112</b></div>",
            unsafe_allow_html=True)


# ── Search & Filters (Moved from Sidebar) ────
with st.expander("🔍 Search & Location Settings", expanded=not st.session_state.get('ph_searched', False)):

    st.markdown("<p class='sb-section'>📍 Location</p>",unsafe_allow_html=True)
    mode=st.radio("M",["🌐 Auto-detect","🔎 City","📌 Coords"],label_visibility="collapsed")
    if mode=="🌐 Auto-detect":
        if st.button("📡 Detect",use_container_width=True):
            with st.spinner("…"): lat,lng,city=detect_ip_location()
            if lat:
                st.session_state.user_lat=lat;st.session_state.user_lng=lng
                st.session_state.location_name=city;st.success(f"✅ {city}")
    elif mode=="🔎 City":
        addr=st.text_input("City",placeholder="e.g. Andheri, Mumbai")
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
    radius=st.slider("Radius (km)",1,20,5)
    filter_24h=st.checkbox("24×7 Only",value=False)
    st.markdown("<hr>",unsafe_allow_html=True)
    no_loc=st.session_state.user_lat is None
    if no_loc: st.caption("⚠️ Set location first.")
    if st.button("💊 Find Pharmacies",use_container_width=True,type="primary",disabled=no_loc):
        with st.spinner("Searching…"):
            result=fetch_pharmacies(st.session_state.user_lat,st.session_state.user_lng,radius)
        if result=="TIMEOUT": st.error("⏱️ Timeout.")
        else:
            if filter_24h:
                result=[p for p in result if "24" in p.get("opening_hours","").lower()]
            st.session_state.pharmacies=[enrich_pharmacy(pharmacy) for pharmacy in result]
            st.session_state.ph_radius=radius
            st.session_state.ph_searched=True; st.rerun()
    st.markdown("<hr>",unsafe_allow_html=True)
    for icon,lbl,num in EMERGENCY_NUMBERS[:4]:
        st.markdown(f"<div class='enum-item'><span class='lbl'>{icon} {lbl}</span>"
                    f"<span class='num'>{num}</span></div>",unsafe_allow_html=True)


if not st.session_state.ph_searched:
    st.info("👈 Set your location and click **Find Pharmacies**."); st.stop()

pharma=[enrich_pharmacy(pharmacy) for pharmacy in st.session_state.pharmacies]
m1,m2,m3=st.columns(3)
m1.metric("💊 Found",  len(pharma))
m2.metric("📍 Nearest",f"{pharma[0]['distance_km']} km" if pharma else "—")
m3.metric("🔍 Radius", f"{st.session_state.ph_radius} km")
st.markdown("---")
if not pharma: st.warning("No pharmacies found. Try larger radius."); st.stop()

tab_availability,tab_map,tab_list,tab_table=st.tabs(["💊 Medicine Availability", "🗺️ Map","📋 List","📊 Table"])
with tab_availability:
    st.markdown("### Check medicine availability")
    st.caption("Availability is based on the latest pharmacy inventory. Call ahead before collecting urgent medicines.")
    medicine_query = st.text_input(
        "Search medicine", placeholder="e.g. Paracetamol, ORS, Cetirizine",
        key="medicine_availability_search"
    )
    availability_rows = []
    for pharmacy in pharma:
        matching_medicines = [medicine for medicine in pharmacy.get("medicines", [])
                              if not medicine_query.strip()
                              or medicine_query.lower() in medicine["name"].lower()]
        for medicine in matching_medicines:
            availability_rows.append((pharmacy, medicine))
    if not availability_rows:
        st.info("No matching medicines were found in the listed pharmacies.")
    else:
        for pharmacy, medicine in availability_rows:
            is_open = pharmacy.get("open_now")
            open_label = pharmacy.get("open_status", "Hours not listed")
            open_badge = "b-green" if is_open is True else "b-red" if is_open is False else "b-orange"
            stock_badge = "b-green" if medicine.get("available") and medicine.get("quantity", 0) > 0 else "b-red"
            stock_label = f"Available · {medicine.get('quantity', 0)} units" if medicine.get("available") else "Out of stock"
            prescription_label = " · Prescription required" if medicine.get("prescription_required") else ""
            st.markdown(f"""
            <div class="h-card pharm">
              <div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;">
                <div>
                  <p class="h-name">💊 {medicine['name']}</p>
                  <p class="h-detail">{medicine.get('category', 'Medicine')}{prescription_label}</p>
                </div>
                <div>
                  <span class="badge {stock_badge}">{stock_label}</span>
                  <span class="badge {open_badge}">{'🟢 Open' if is_open is True else '🔴 Closed' if is_open is False else '🕐'} {open_label}</span>
                </div>
              </div>
              <p class="h-detail"><b>{pharmacy['name']}</b> · {pharmacy.get('address', '')}</p>
              <p class="h-detail">📍 {pharmacy.get('distance_km', '—')} km · 📞 {pharmacy.get('phone', 'Not listed')}</p>
            </div>""", unsafe_allow_html=True)
            if medicine.get("available") and is_open is not False:
                with st.expander(f"🛒 Order {medicine['name']} from {pharmacy['name']}"):
                    order_address = st.text_input(
                        "Delivery or pickup address",
                        key=f"availability_address_{pharmacy['name']}_{medicine['name']}"
                    )
                    order_quantity = st.number_input(
                        "Quantity", min_value=1, max_value=medicine.get("quantity", 1), value=1,
                        key=f"availability_quantity_{pharmacy['name']}_{medicine['name']}"
                    )
                    if st.button(
                        "Place medicine order",
                        type="primary",
                        key=f"availability_order_{pharmacy['name']}_{medicine['name']}"
                    ):
                        if not order_address.strip():
                            st.warning("Please enter a delivery or pickup address.")
                        else:
                            from utils.chat_db import create_medicine_order
                            order = create_medicine_order(
                                st.session_state.user_email,
                                st.session_state.get("user_name", "Patient"),
                                pharmacy["name"],
                                f"{medicine['name']} x {order_quantity}",
                                order_address,
                                "Ordered from Medicine Availability"
                            )
                            st.success(f"Order {order['id']} submitted successfully.")
            elif not medicine.get("available"):
                st.caption("Ordering is unavailable because this medicine is out of stock.")
            else:
                st.caption("This pharmacy is currently closed. Ordering will be available when it opens.")
with tab_map:
    st_folium(build_pharmacy_map(pharma,st.session_state.user_lat,st.session_state.user_lng),
              use_container_width=True,height=480)
    st.caption("🔵 You · 🟢 Pharmacy")
with tab_list:
    sq=st.text_input("🔎 Filter",placeholder="Pharmacy name…")
    disp=[p for p in pharma if sq.lower() in p["name"].lower()] if sq else pharma
    for p in disp:
        dir_url=directions_url(p["lat"],p["lng"],st.session_state.user_lat,st.session_state.user_lng)
        is24="24" in p.get("opening_hours","") or "nonstop" in p.get("opening_hours","").lower()
        b24=("<span class='badge b-green'>🕐 24×7</span>" if is24
             else (f"<span class='badge b-orange'>🕐 {p['opening_hours']}</span>" if p["opening_hours"] else ""))
        open_badge = ("<span class='badge b-green'>🟢 Open now</span>" if p.get("open_now") is True
                  else "<span class='badge b-red'>🔴 Closed now</span>" if p.get("open_now") is False else "")
        st.markdown(f"""
        <div class="h-card pharm">
          <div style="display:flex;justify-content:space-between;flex-wrap:wrap;">
            <p class="h-name">💊 {p["name"]}</p>
            <span class="badge b-dist">📍 {p["distance_km"]} km</span>
          </div>
          <p class="h-detail">📋 {p["address"]}</p>
          {"<p class='h-detail'>📞 "+p["phone"]+"</p>" if p["phone"] else ""}
          <div style="margin-top:6px;">{open_badge}{b24}</div>
          <div style="margin-top:10px;">
            <a class="action-btn btn-dir" href="{dir_url}" target="_blank">🗺️ Directions</a>
            {"<a class='action-btn btn-call' href='tel:"+p["phone"]+"'>📞 Call</a>" if p["phone"] else ""}
          </div>
        </div>""",unsafe_allow_html=True)
        
        # Pharmacy Interaction (Patient ordering / receiving prescription slip)
        with st.expander("💬 Interact / Order from this Pharmacy"):
            from utils.chat_db import (get_pharmacy_interaction, add_pharmacy_interaction,
                                       create_medicine_order)
            email = st.session_state.user_email
            if not email:
                st.warning("Please log in to interact with pharmacies.")
            else:
                p_name = p["name"]
                st.markdown("#### Place a Medicine Order")
                order_items = st.text_area(
                    "Medicines or prescription items",
                    placeholder="Medicine name, strength, quantity",
                    key=f"order_items_{p_name}"
                )
                delivery_address = st.text_input(
                    "Delivery or pickup address", key=f"order_address_{p_name}"
                )
                order_notes = st.text_input(
                    "Notes for the pharmacist (optional)", key=f"order_notes_{p_name}"
                )
                if st.button("Submit medicine order", type="primary", key=f"order_{p_name}"):
                    if not order_items.strip() or not delivery_address.strip():
                        st.warning("Medicine items and an address are required.")
                    else:
                        order = create_medicine_order(
                            email, st.session_state.get("user_name", "Patient"),
                            p_name, order_items, delivery_address, order_notes
                        )
                        st.success(f"Order {order['id']} received by {p_name}.")

                st.markdown("#### Pharmacy Chat")
                history = get_pharmacy_interaction(email, p_name)
                for msg in history:
                    with st.chat_message("user" if msg["sender"] == "Patient" else "assistant"):
                        st.markdown(f"**{msg['sender']}** ({msg['timestamp']})")
                        st.write(msg["text"])
                
                # Chat input
                new_msg = st.text_input("Send your order/prescription request:", key=f"chat_{p_name}")
                if st.button("Send", key=f"btn_chat_{p_name}") and new_msg.strip():
                    # Patient message
                    add_pharmacy_interaction(email, p_name, new_msg.strip(), is_bot=False)
                    # Simulated pharmacy response
                    reply = (f"✅ Order received! We have processed your request for '{new_msg.strip()[:20]}...'. "
                             f"Your prescription/bill has been generated. You can pick it up in 15 minutes.")
                    add_pharmacy_interaction(email, p_name, reply, is_bot=True)
                    st.rerun()

with tab_table:
    df=pd.DataFrame([{"Name":p["name"],"Distance (km)":p["distance_km"],
        "Phone":p["phone"] or "—","Opening Hours":p["opening_hours"] or "—"} for p in pharma])
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("⬇️ CSV",df.to_csv(index=False),"pharmacies.csv","text/csv")

st.markdown("---")
st.markdown("### 📦 My Medicine Orders")
from utils.chat_db import (get_all_medicine_orders, get_medicine_orders,
                           update_medicine_order_status)
if st.session_state.get("user_role") == "admin":
    orders = get_all_medicine_orders()
else:
    orders = get_medicine_orders(st.session_state.get("user_email", ""))
if not orders:
    st.info("No medicine orders yet.")
else:
    for order in reversed(orders):
        with st.expander(f"{order['id']} · {order['pharmacy_name']} · {order['status']}"):
            st.write(f"**Items:** {order['items']}")
            st.write(f"**Address:** {order['delivery_address']}")
            if order.get("notes"):
                st.write(f"**Notes:** {order['notes']}")
            st.caption(f"Placed {order['created_at']}")
            if st.session_state.get("user_role") == "admin":
                statuses = ["Received", "Processing", "Ready for pickup", "Out for delivery", "Delivered", "Cancelled"]
                new_status = st.selectbox(
                    "Update status", statuses, index=statuses.index(order["status"]),
                    key=f"order_status_{order['id']}"
                )
                if st.button("Save order status", key=f"save_order_status_{order['id']}"):
                    update_medicine_order_status(order["id"], new_status)
                    st.rerun()
