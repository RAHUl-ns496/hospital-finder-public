import streamlit as st

from utils.auth import check_auth, get_all_users
from utils.chat_db import get_patients_for_doctor
from utils.styles import COMMON_CSS

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["doctor"])

email = st.session_state.get("user_email", "")
users = get_all_users()
patient_emails = get_patients_for_doctor(email)

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">👥</div>
  <div><h1>Assigned Patients</h1>
       <p>Review patient information before a consultation</p></div>
</div>""", unsafe_allow_html=True)

if not patient_emails:
    st.info("No patients are assigned to you yet.")
    st.stop()

search = st.text_input("Search assigned patients", placeholder="Name or email")
for patient_email in patient_emails:
    patient = users.get(patient_email, {})
    searchable = f"{patient.get('name', '')} {patient_email}".lower()
    if search.strip().lower() not in searchable:
        continue

    with st.container(border=True):
        st.markdown(f"### 👤 {patient.get('name', patient_email)}")
        st.caption(patient_email)
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Blood type**\n\n{patient.get('blood_type', 'Unknown')}")
        c2.write(f"**Allergies**\n\n{patient.get('allergies', 'None recorded')}")
        c3.write(f"**Conditions**\n\n{patient.get('conditions', 'None recorded')}")

        records = patient.get("medical_records", [])
        if records:
            with st.expander(f"Medical records ({len(records)})"):
                for record in records:
                    st.write(f"**{record.get('date', 'Undated')} · {record.get('title', 'Record')}**")
                    st.write(record.get("details", "No details provided."))
        contacts = patient.get("emergency_contacts", [])
        if contacts:
            with st.expander("Emergency contacts"):
                for contact in contacts:
                    st.write(f"{contact.get('name', 'Contact')} · {contact.get('relation', 'Other')} · {contact.get('phone', '')}")

        st.page_link("pages/8_Consultations.py", label="💬 Open consultation workspace", use_container_width=True)
