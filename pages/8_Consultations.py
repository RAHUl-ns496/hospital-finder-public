import streamlit as st
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils.styles import COMMON_CSS
from utils.auth import get_all_users
from utils.chat_db import (get_assignment, set_assignment, get_patients_for_doctor,
                           get_messages, get_prescriptions, send_message, get_appointments)

st.markdown(COMMON_CSS, unsafe_allow_html=True)

role = st.session_state.get("user_role")
email = st.session_state.get("user_email")

if not email or role not in ["patient", "doctor", "admin"]:
    st.warning("Please log in to access Consultations.")
    st.stop()

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">💬</div>
  <div><h1>Doctor Consultations</h1>
       <p>Secure messaging between patients and assigned doctors</p></div>
</div>""", unsafe_allow_html=True)

users_db = get_all_users()

def render_downloads(messages, prescriptions, download_key):
    if not messages:
        return
    chat_text = "\n".join(
        f"[{message['timestamp']}] {message['sender']}: {message['text']}"
        + (" [PRESCRIPTION]" if message.get("is_prescription") else "")
        for message in messages
    )
    download_cols = st.columns(3)
    download_cols[0].download_button(
        "⬇️ Download chat",
        chat_text,
        file_name="consultation_chat.txt",
        mime="text/plain",
        key=f"chat_download_{download_key}",
    )
    download_cols[1].download_button(
        "⬇️ Chat JSON",
        json.dumps(messages, indent=2, ensure_ascii=False),
        file_name="consultation_chat.json",
        mime="application/json",
        key=f"chat_json_download_{download_key}",
    )
    if prescriptions:
        prescription_text = "\n\n".join(
            f"Prescription date: {message['timestamp']}\n"
            f"Prescribed by: {message['sender']}\n"
            f"Instructions: {message['text']}"
            for message in prescriptions
        )
        download_cols[2].download_button(
            "📄 Download prescriptions",
            prescription_text,
            file_name="prescriptions.txt",
            mime="text/plain",
            key=f"prescription_download_{download_key}",
        )
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        pdf.setTitle("Medical Prescriptions")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 750, "Medical Prescription Record")
        y = 720
        pdf.setFont("Helvetica", 10)
        for prescription in prescriptions:
            lines = [
                f"Date: {prescription['timestamp']}",
                f"Prescribed by: {prescription['sender']}",
                f"Instructions: {prescription['text']}",
                "",
            ]
            for line in lines:
                for part in [line[index:index + 95] for index in range(0, len(line), 95)] or [""]:
                    if y < 60:
                        pdf.showPage()
                        pdf.setFont("Helvetica", 10)
                        y = 750
                    pdf.drawString(50, y, part)
                    y -= 16
        pdf.save()
        download_cols[2].download_button(
            "📄 Prescription PDF", pdf_buffer.getvalue(),
            file_name="prescriptions.pdf", mime="application/pdf",
            key=f"prescription_pdf_{download_key}",
        )

st.markdown("### 📅 Appointments")
appointments = get_appointments(email, role)
if appointments:
    for appointment in appointments:
        other_email = appointment["doctor_email"] if role == "patient" else appointment["patient_email"]
        other = users_db.get(other_email, {})
        other_name = other.get("name", other_email)
        label = f"Dr. {other_name}" if role == "patient" else other_name
        st.info(f"{appointment['date']} at {appointment['time']} · {label} · {appointment.get('appointment_type', 'In-person visit')} · {appointment['status']} · {appointment['reason']}")
else:
    st.caption("No appointments booked yet. Use Find Doctors to book one.")

if role == "patient" or st.session_state.get("is_guest"):
    st.markdown("### My Doctor")
    assigned_doc = get_assignment(email)
    
    if not assigned_doc:
        st.info("You do not have a doctor assigned yet. Please select a doctor for consultation.")
        docs = {e: u for e, u in users_db.items() if u.get("role") == "doctor"}
        if not docs:
            st.error("No doctors available in the system right now.")
        else:
            doc_options = {e: f"Dr. {u.get('name')} ({u.get('department', 'General')})" for e, u in docs.items()}
            selected_doc = st.selectbox("Choose a Doctor:", list(doc_options.keys()), format_func=lambda x: doc_options[x])
            if st.button("Request Assignment", type="primary"):
                set_assignment(email, selected_doc)
                st.success(f"Assigned to {doc_options[selected_doc]}.")
                st.rerun()
    else:
        doc_info = users_db.get(assigned_doc, {})
        doc_name = doc_info.get("name", "Unknown Doctor")
        st.markdown(f"**Assigned Doctor:** Dr. {doc_name} ({doc_info.get('department', '')} - {doc_info.get('hospital', '')})")
        if st.button("Change Doctor"):
            set_assignment(email, None)
            st.rerun()
            
        st.markdown("---")
        st.markdown("### Consultation Chat")
        msgs = get_messages(email, assigned_doc)
        prescriptions = get_prescriptions(email, assigned_doc)
        
        chat_container = st.container(height=400)
        with chat_container:
            if not msgs:
                st.caption("No messages yet. Send a message to start the consultation.")
            for m in msgs:
                is_me = (m["sender"] == email)
                with st.chat_message("user" if is_me else "assistant"):
                    sender_name = "You" if is_me else f"Dr. {doc_name}"
                    st.markdown(f"**{sender_name}** ({m['timestamp']})")
                    if m.get("is_prescription"):
                        st.markdown(f"<div style='background:#e3f2fd;padding:10px;border-left:4px solid #1976d2;border-radius:4px;'><b>📄 PRESCRIPTION:</b><br>{m['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.write(m["text"])

        render_downloads(msgs, prescriptions, f"patient_{email}_{assigned_doc}")
        
        new_msg = st.chat_input("Type your message here...")
        if new_msg:
            send_message(email, assigned_doc, new_msg, is_prescription=False)
            st.rerun()

elif role == "doctor" or role == "admin":
    # If admin, let them pick a doctor to view as
    if role == "admin":
        st.info("Admin Mode: Viewing as Doctor")
        docs = [e for e, u in users_db.items() if u.get("role") == "doctor"]
        if not docs:
            st.error("No doctors exist."); st.stop()
        active_doc = st.selectbox("Select Doctor View:", docs, format_func=lambda x: users_db[x].get("name"))
    else:
        active_doc = email

    st.markdown("### Assigned Patients")
    patients = get_patients_for_doctor(active_doc)
    
    if not patients:
        st.info("You have no patients assigned to you currently.")
    else:
        patient_options = {p: users_db.get(p, {}).get("name", p) for p in patients}
        selected_patient = st.selectbox("Select Patient to Chat:", list(patient_options.keys()), format_func=lambda x: patient_options[x])
        
        st.markdown("---")
        st.markdown(f"### Chat with {patient_options[selected_patient]}")
        
        msgs = get_messages(active_doc, selected_patient)
        prescriptions = get_prescriptions(active_doc, selected_patient)
        chat_container = st.container(height=400)
        with chat_container:
            if not msgs:
                st.caption("No messages yet.")
            for m in msgs:
                is_me = (m["sender"] == active_doc)
                with st.chat_message("assistant" if is_me else "user"):
                    sender_name = "You" if is_me else patient_options[selected_patient]
                    st.markdown(f"**{sender_name}** ({m['timestamp']})")
                    if m.get("is_prescription"):
                        st.markdown(f"<div style='background:#e3f2fd;padding:10px;border-left:4px solid #1976d2;border-radius:4px;'><b>📄 PRESCRIPTION:</b><br>{m['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.write(m["text"])

        render_downloads(msgs, prescriptions, f"doctor_{active_doc}_{selected_patient}")
        
        is_presc = st.checkbox("Send as Medical Prescription 📄")
        new_msg = st.chat_input("Type your message or prescription here...")
        if new_msg:
            send_message(active_doc, selected_patient, new_msg, is_prescription=is_presc)
            st.rerun()
