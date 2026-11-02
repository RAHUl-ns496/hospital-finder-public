import streamlit as st
from datetime import date, timedelta

from utils.auth import check_auth, get_all_users
from utils.chat_db import (create_appointment, get_appointments, get_doctor_slots,
                           update_appointment_status)
from utils.styles import COMMON_CSS

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth()

email = st.session_state.get("user_email", "")
role = st.session_state.get("user_role", "patient")
users = get_all_users()

def doctor_profile(doctor_email, user):
    department = user.get("department") or "General Medicine"
    hospital = user.get("hospital") or "Emergency Hospital"
    specialties = [item.strip() for item in department.split("/") if item.strip()]
    return {
        "email": doctor_email,
        "name": user.get("name", "Doctor"),
        "department": department,
        "hospital": hospital,
        "phone": user.get("phone", ""),
        "specialties": specialties,
        "experience": user.get("experience", "8+ years"),
        "fee": user.get("consultation_fee", "₹500"),
        "languages": user.get("languages", "English, Hindi"),
        "rating": user.get("rating", "4.8"),
    }


doctors = [doctor_profile(e, u) for e, u in users.items()
           if u.get("role") == "doctor" and u.get("active", True)]

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">🩺</div>
  <div><h1>Find a Doctor</h1>
       <p>Search verified care providers, review their profiles, and book an appointment</p></div>
</div>""", unsafe_allow_html=True)

st.markdown("<div class='page-kicker'>Verified care providers</div>", unsafe_allow_html=True)

if not doctors:
    st.info("No active doctors are available right now.")
    st.stop()

fc1, fc2, fc3 = st.columns([2, 1.4, 1.2])
with fc1:
    query = st.text_input("Search doctors", placeholder="Name, specialty, or hospital")
with fc2:
    departments = sorted({d["department"] for d in doctors})
    department = st.selectbox("Specialty", ["All"] + departments)
with fc3:
    sort_by = st.selectbox("Sort by", ["Rating", "Name", "Consultation fee"])

filtered = [d for d in doctors if (
    not query.strip()
    or query.lower() in d["name"].lower()
    or query.lower() in d["department"].lower()
    or query.lower() in d["hospital"].lower()
) and (department == "All" or d["department"] == department)]
if sort_by == "Name":
    filtered.sort(key=lambda d: d["name"].lower())
elif sort_by == "Consultation fee":
    filtered.sort(key=lambda d: d["fee"])
else:
    filtered.sort(key=lambda d: d["rating"], reverse=True)

st.markdown(f"<div class='results-summary'><strong>{len(filtered)} doctors</strong> available for consultation</div>", unsafe_allow_html=True)
for doctor in filtered:
    with st.container(border=True):
        left, right = st.columns([4, 1.2])
        with left:
            st.markdown(f"### 🩺 Dr. {doctor['name']}")
            st.write(f"**{doctor['department']}** · {doctor['hospital']}")
            st.write(f"⭐ {doctor['rating']} · {doctor['experience']} · Languages: {doctor['languages']}")
            st.write(f"Specialties: {', '.join(doctor['specialties'])}")
        with right:
            st.metric("Consultation", doctor["fee"])
            with st.expander("View profile"):
                st.write(f"**Qualification:** {doctor.get('qualification', 'Verified medical professional')}")
                st.write(f"**Experience:** {doctor['experience']}")
                st.write(f"**Languages:** {doctor['languages']}")
                st.write(f"**Hospital:** {doctor['hospital']}")

        with st.expander(f"Book with Dr. {doctor['name']}"):
            if st.session_state.get("is_guest"):
                st.warning("Please create an account before booking an appointment.")
            else:
                appointment_date = st.date_input(
                    "Appointment date", min_value=date.today(),
                    value=date.today() + timedelta(days=1),
                    key=f"date_{doctor['email']}"
                )
                doctor_slots = get_doctor_slots(doctor["email"])
                slot_options = sorted({slot["time"] for slot in doctor_slots
                                       if slot["date"] == appointment_date.isoformat()})
                if not slot_options:
                    st.info("This doctor has no open slots for that date.")
                    continue
                appointment_time = st.selectbox("Available time slot", slot_options,
                                                key=f"time_{doctor['email']}")
                appointment_type = st.selectbox(
                    "Appointment option",
                    ["In-person visit", "Video consultation", "Audio consultation", "Home visit"],
                    key=f"type_{doctor['email']}"
                )
                reason = st.text_area(
                    "Reason for visit", placeholder="Briefly describe what you need help with",
                    key=f"reason_{doctor['email']}"
                )
                if st.button("Confirm appointment", type="primary", key=f"book_{doctor['email']}"):
                    if not reason.strip():
                        st.warning("Please add a reason for the appointment.")
                    else:
                        appointment = create_appointment(
                            email, doctor["email"], appointment_date.isoformat(),
                            appointment_time, reason, st.session_state.get("user_name", ""),
                            appointment_type
                        )
                        if appointment:
                            st.success(f"Request {appointment['id']} submitted for {appointment_date} at {appointment_time}.")
                        else:
                            st.error("That slot was just taken. Please choose another time.")

st.markdown("---")
st.markdown("### My Appointments")
appointments = get_appointments(email)
if not appointments:
    st.info("You have no appointments yet.")
else:
    for appointment in sorted(appointments, key=lambda item: (item["date"], item["time"])):
        doctor = users.get(appointment["doctor_email"], {})
        name = doctor.get("name", appointment["doctor_email"])
        c1, c2, c3, c4 = st.columns([2.2, 1.3, 1.2, 1])
        c1.write(f"**Dr. {name}**\n\n{appointment.get('appointment_type', 'In-person visit')}\n\n{appointment['reason']}")
        c2.write(f"{appointment['date']}\n\n{appointment['time']}")
        c3.write(appointment["status"])
        if appointment["status"] in ["Pending", "Approved"] and c4.button("Cancel", key=f"cancel_{appointment['id']}"):
            update_appointment_status(appointment["id"], "Cancelled")
            st.rerun()
