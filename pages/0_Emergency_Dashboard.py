import streamlit as st
from utils.auth import check_auth
from utils.chat_db import get_appointments
from utils.chat_db import get_notifications, mark_notifications_read
from utils.helpers import EMERGENCY_NUMBERS
from utils.styles import COMMON_CSS

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth()

email = st.session_state.get("user_email", "")
name = st.session_state.get("user_name", "User")
appointments = get_appointments(email, st.session_state.get("user_role"))
upcoming = [appointment for appointment in appointments
            if appointment["status"] in ["Pending", "Approved", "Booked"]]

st.markdown(f"""
<div class="app-header">
  <div style="font-size:50px;">🚨</div>
  <div><h1>Emergency Health Dashboard</h1>
       <p>Fast access to care, medical information, and trusted support for {name}</p></div>
</div>""", unsafe_allow_html=True)

st.markdown("<div class='page-kicker'>Your care, in one place</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'><div><h2>Need help right now?</h2><p>Reach emergency services or find the right care in seconds.</p></div></div>", unsafe_allow_html=True)
emergency_cols = st.columns(4)
for column, (icon, label, number) in zip(emergency_cols, EMERGENCY_NUMBERS[:4]):
    with column:
        st.markdown(f"**{icon} {label}**\n\n### {number}")
        st.link_button(f"Call {number}", f"tel:{number}", use_container_width=True)

st.markdown("---")
st.markdown("<div class='section-title'><div><h2>Find care quickly</h2><p>Search trusted hospitals, doctors, pharmacies, and blood banks.</p></div></div>", unsafe_allow_html=True)
care_cols = st.columns(4)
care_actions = [
    ("🏥", "Find Hospitals", "pages/1_Find_Hospitals.py"),
    ("🩸", "Find Blood Banks", "pages/2_Blood_Bank.py"),
    ("💊", "Find Pharmacies", "pages/3_Pharmacy.py"),
    ("🆘", "First Aid Guide", "pages/4_First_Aid_Guide.py"),
]
for column, (icon, label, page) in zip(care_cols, care_actions):
    with column:
        st.page_link(page, label=f"{icon} {label}", use_container_width=True)

st.markdown("<div class='section-title'><div><h2>Your care at a glance</h2><p>A quick view of the information you use most.</p></div></div>", unsafe_allow_html=True)
summary_cols = st.columns(4)
summary_cols[0].metric("📅 Appointments", len(upcoming))
summary_cols[1].metric("🏥 Saved hospitals", len(st.session_state.get("saved_hospitals", [])))
summary_cols[2].metric("📞 Emergency contacts", len(st.session_state.get("emergency_contacts", [])))
summary_cols[3].metric("🩸 Blood type", st.session_state.get("user_blood_type") or "Unknown")

st.markdown("<div class='section-title'><div><h2>🔔 Notifications</h2><p>Updates about appointments and medicine orders.</p></div></div>", unsafe_allow_html=True)
notifications = get_notifications(email)
unread = [notification for notification in notifications if not notification.get("read")]
if unread:
    st.info(f"You have {len(unread)} unread notification(s).")
    if st.button("Mark notifications as read"):
        mark_notifications_read(email)
        st.rerun()
for notification in notifications[:5]:
    message = f"**{notification['title']}**\n\n{notification['message']}"
    if notification.get("read"):
        st.caption(message)
    else:
        st.warning(message)

left, right = st.columns(2)
with left:
    st.markdown("### Upcoming appointments")
    if not upcoming:
        st.info("No upcoming appointments. Use Find a Doctor to book one.")
    else:
        users = __import__("utils.auth", fromlist=["get_all_users"]).get_all_users()
        for appointment in upcoming[:3]:
            doctor = users.get(appointment["doctor_email"], {})
            st.info(
                f"**Dr. {doctor.get('name', 'Doctor')}**\n\n"
                f"{appointment['date']} at {appointment['time']} · {appointment['reason']}"
            )
with right:
    st.markdown("### Medical ID snapshot")
    st.warning(
        f"**Blood type:** {st.session_state.get('user_blood_type') or 'Unknown'}\n\n"
        f"**Allergies:** {st.session_state.get('user_allergies') or 'None recorded'}\n\n"
        f"**Conditions:** {st.session_state.get('user_conditions') or 'None recorded'}"
    )
    st.page_link("pages/5_My_Profile.py", label="Open full medical profile", icon="👤")

st.markdown("---")
st.markdown("### More support")
support_cols = st.columns(3)
with support_cols[0]:
    st.page_link("pages/8_Consultations.py", label="💬 Chat with a doctor", use_container_width=True)
with support_cols[1]:
    st.page_link("pages/4_First_Aid_Guide.py", label="🆘 First-aid guide", use_container_width=True)
with support_cols[2]:
    st.page_link("pages/9_Symptom_Checker.py", label="🔍 Check symptoms", use_container_width=True)

st.caption("For life-threatening emergencies, call emergency services immediately. This app does not replace professional medical care.")
