import streamlit as st

from utils.auth import check_auth, get_all_users
from utils.chat_db import get_appointments, get_patients_for_doctor
from utils.healthcare_db import get_hospital_capacity
from utils.styles import COMMON_CSS

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["doctor"])

email = st.session_state.get("user_email", "")
users = get_all_users()
user = users.get(email, {})
patients = get_patients_for_doctor(email)
appointments = get_appointments(email, "doctor")
capacity = get_hospital_capacity(user.get("hospital", "")) if user.get("hospital") else None

st.markdown(f"""
<div class="app-header">
  <div style="font-size:50px;">🩺</div>
  <div><h1>Doctor Dashboard</h1>
       <p>Welcome back, Dr. {user.get('name', 'Doctor')} · {user.get('hospital', 'Hospital workspace')}</p></div>
</div>""", unsafe_allow_html=True)

st.markdown("<div class='page-kicker'>Clinical workspace</div>", unsafe_allow_html=True)
metrics = st.columns(4)
metrics[0].metric("Assigned patients", len(patients))
metrics[1].metric("Pending requests", sum(1 for a in appointments if a["status"] == "Pending"))
metrics[2].metric("Approved appointments", sum(1 for a in appointments if a["status"] == "Approved"))
metrics[3].metric("Available ICU beds", capacity.get("icu_available", "—") if capacity else "—")

st.markdown("### Today at a glance")
today = [a for a in appointments if a["status"] in ["Pending", "Approved"]]
if not today:
    st.info("No active appointment requests. Your assigned patients will appear below.")
else:
    for appointment in today[:6]:
        patient = users.get(appointment["patient_email"], {})
        st.info(
            f"**{patient.get('name', appointment['patient_email'])}** · "
            f"{appointment['date']} at {appointment['time']} · "
            f"{appointment.get('appointment_type', 'In-person visit')} · {appointment['status']}"
        )

st.markdown("### Assigned patient preview")
if not patients:
    st.info("No patients are assigned to you yet.")
else:
    for patient_email in patients[:5]:
        patient = users.get(patient_email, {})
        c1, c2, c3 = st.columns([2.5, 2, 1])
        c1.write(f"**{patient.get('name', patient_email)}**\n\n{patient_email}")
        c2.write(
            f"Blood: {patient.get('blood_type', 'Unknown')}\n\n"
            f"Conditions: {patient.get('conditions', 'None recorded')}"
        )
        c3.page_link("pages/12_Assigned_Patients.py", label="Open profile", icon="👤")

st.markdown("---")
st.page_link("pages/12_Assigned_Patients.py", label="👥 View all assigned patients", use_container_width=True)
st.page_link("pages/6_Doctor_Panel.py", label="⚙️ Manage availability and capacity", use_container_width=True)
