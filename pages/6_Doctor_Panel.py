import streamlit as st
import random
import pandas as pd
from datetime import datetime, timedelta
from utils.styles import COMMON_CSS
from utils.auth import get_all_users
from utils.chat_db import (get_appointments, get_doctor_slots, set_doctor_slots,
                           update_appointment_status, get_shift_notes, save_shift_notes)
from utils.healthcare_db import get_hospital_capacity, update_hospital_capacity

st.markdown(COMMON_CSS, unsafe_allow_html=True)
from utils.auth import check_auth

check_auth(required_roles=["admin", "doctor"])

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">🩺</div>
  <div><h1>Doctor Panel</h1>
       <p>Hospital capacity dashboard · Shift notes · Patient queue</p></div>
</div>""", unsafe_allow_html=True)

email = st.session_state.get("user_email", "")
user = get_all_users().get(email, {})

st.markdown("### 📆 Doctor Availability")
availability_date = st.date_input("Available date", key="availability_date")
available_times = st.multiselect(
    "Open time slots", ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    default=["10:00", "14:00"], key="availability_times"
)
if st.button("Save availability", type="primary"):
    set_doctor_slots(email, [
        {"date": availability_date.isoformat(), "time": time}
        for time in available_times
    ])
    st.success("Availability saved.")

st.caption(f"Open slots: {len(get_doctor_slots(email))}")
st.markdown("---")
st.markdown("### 🏥 Hospital Capacity Status")

hospital_name = user.get("hospital", "")
capacity = get_hospital_capacity(hospital_name) if hospital_name else None
if capacity:
    bed_col, icu_col, vent_col = st.columns(3)
    beds = bed_col.number_input("Available ER beds", min_value=0, value=int(capacity.get("beds_available", 0)), key="capacity_beds")
    icu = icu_col.number_input("Available ICU beds", min_value=0, value=int(capacity.get("icu_available", 0)), key="capacity_icu")
    vents = vent_col.number_input("Available ventilators", min_value=0, value=int(capacity.get("ventilators_available", 0)), key="capacity_vents")
    if st.button("Update hospital capacity", key="update_capacity"):
        update_hospital_capacity(hospital_name, beds, icu, vents)
        st.success("Hospital capacity updated.")
else:
    st.info("No seeded capacity record matches your hospital. Add the hospital to MongoDB first.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Available ER Beds", capacity.get("beds_available", "—") if capacity else "—")
col2.metric("Available ICU Beds", capacity.get("icu_available", "—") if capacity else "—")
col3.metric("Ventilators", capacity.get("ventilators_available", "—") if capacity else "—")
col4.metric("Active Ambulances", "Live data unavailable")

st.markdown("---")
st.markdown("### 📅 Appointment Requests")
appointments = get_appointments(email, "doctor")
for appointment in appointments:
    c1, c2, c3 = st.columns([3, 1.2, 1.5])
    c1.write(f"**{appointment['patient_name']}** · {appointment['reason']}")
    c2.write(f"{appointment['date']} {appointment['time']}")
    if appointment["status"] == "Pending":
        with c3:
            if st.button("Approve", key=f"approve_{appointment['id']}"):
                update_appointment_status(appointment["id"], "Approved")
                st.rerun()
            if st.button("Decline", key=f"decline_{appointment['id']}"):
                update_appointment_status(appointment["id"], "Declined")
                st.rerun()
    else:
        c3.write(appointment["status"])

st.markdown("---")
st.markdown("### 📝 Shift Notes")
shift_notes = st.text_area("Enter notes for the current shift:",
                           value=get_shift_notes(email), height=150, key="doctor_shift_notes")
if st.button("Save Notes", type="primary"):
    save_shift_notes(email, shift_notes)
    st.success("Notes saved for this shift.")

st.markdown("---")
st.markdown("### 🚑 Incoming Patients (Simulated)")
df = pd.DataFrame({
    "Time": [(datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime("%H:%M") for _ in range(5)],
    "Condition": ["Trauma", "Cardiac", "Burn", "Respiratory", "Fracture"],
    "ETA (mins)": [random.randint(2, 25) for _ in range(5)],
    "Priority": ["High", "Critical", "Medium", "High", "Low"]
}).sort_values("ETA (mins)")

st.dataframe(df, use_container_width=True, hide_index=True)
