import streamlit as st
import json
from datetime import date
from utils.styles import COMMON_CSS
from utils.helpers import BLOOD_TYPES
from utils.auth import _load_db, _save_db, update_user_fields, check_auth

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["patient"])

email = st.session_state.get("user_email", "")
if not email:
    st.warning("Please log in to access your profile.")
    st.stop()

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">👤</div>
  <div><h1>My Profile</h1>
       <p>Medical information · Emergency contacts · Saved hospitals · Medical ID</p></div>
</div>""", unsafe_allow_html=True)

db = _load_db()
user = db.get(email, {})

# Initialize session state for contacts
if "emergency_contacts" not in st.session_state:
    st.session_state.emergency_contacts = user.get("emergency_contacts", [])
if "saved_hospitals" not in st.session_state:
    st.session_state.saved_hospitals = user.get("saved_hospitals", [])

tab_profile, tab_contacts, tab_records, tab_family, tab_saved, tab_id = st.tabs(
    ["🏥 Medical Profile", "📞 Emergency Contacts", "🗂️ Medical Records",
     "👨‍👩‍👧 Family Profiles", "💾 Saved Hospitals", "🪪 Medical ID Card"])

# ── Tab 1: Medical Profile ─────────────────────
with tab_profile:
    st.markdown("### Edit Your Medical Profile")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name", value=user.get("name", ""))
        phone = st.text_input("Phone", value=user.get("phone", ""))
        dob = st.date_input("Date of Birth",
                            value=date.fromisoformat(user["dob"]) if user.get("dob") else date(2000, 1, 1),
                            min_value=date(1920, 1, 1), max_value=date.today())
        gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                              index=["Male", "Female", "Other"].index(user.get("gender", "Male"))
                              if user.get("gender") in ["Male", "Female", "Other"] else 0)
    with c2:
        blood_opts = ["Unknown"] + list(BLOOD_TYPES)
        cur_blood = user.get("blood_type", "Unknown")
        blood = st.selectbox("Blood Type", blood_opts,
                             index=blood_opts.index(cur_blood) if cur_blood in blood_opts else 0)
        height_cm = st.number_input("Height (cm)", min_value=50, max_value=250,
                                    value=int(user.get("height_cm", 170)))
        weight_kg = st.number_input("Weight (kg)", min_value=10, max_value=300,
                                    value=int(user.get("weight_kg", 70)))
        # BMI
        bmi = weight_kg / ((height_cm / 100) ** 2) if height_cm > 0 else 0
        if bmi < 18.5:
            bmi_cat = "Underweight"
        elif bmi < 25:
            bmi_cat = "Normal"
        elif bmi < 30:
            bmi_cat = "Overweight"
        else:
            bmi_cat = "Obese"
        st.metric("BMI", f"{bmi:.1f}", bmi_cat)

    allergies = st.text_area("Allergies", value=user.get("allergies", ""), placeholder="e.g. Penicillin, Peanuts")
    conditions = st.text_area("Pre-existing Conditions", value=user.get("conditions", ""),
                              placeholder="e.g. Diabetes, Hypertension, Asthma")

    if st.button("💾 Save Profile", type="primary", use_container_width=True):
        db = _load_db()
        if email in db:
            db[email]["name"] = name
            db[email]["phone"] = phone
            db[email]["dob"] = dob.isoformat()
            db[email]["gender"] = gender
            db[email]["blood_type"] = blood
            db[email]["height_cm"] = height_cm
            db[email]["weight_kg"] = weight_kg
            db[email]["allergies"] = allergies
            db[email]["conditions"] = conditions
            db[email]["emergency_contacts"] = st.session_state.emergency_contacts
            db[email]["saved_hospitals"] = st.session_state.saved_hospitals
            _save_db(db)
            st.session_state.user_name = name
            st.session_state.user_phone = phone
            st.session_state.user_blood_type = blood
            st.session_state.user_conditions = conditions
            st.session_state.user_allergies = allergies
            st.success("✅ Profile saved successfully!")
        else:
            st.error("User not found in database.")

# ── Tab 2: Emergency Contacts ──────────────────
with tab_contacts:
    st.markdown("### 📞 Emergency Contacts")
    contacts = st.session_state.emergency_contacts

    if not contacts:
        st.info("No emergency contacts added yet. Add one below.")
    else:
        for i, c in enumerate(contacts):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.text(c["name"])
            col2.text(c["phone"])
            col3.text(c["relation"])
            if col4.button("🗑️", key=f"del_contact_{i}"):
                contacts.pop(i)
                st.session_state.emergency_contacts = contacts
                update_user_fields(email, {"emergency_contacts": contacts})
                st.rerun()

    st.markdown("---")
    st.markdown("#### ➕ Add New Contact")
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        c_name = st.text_input("Contact Name", key="new_c_name")
    with ac2:
        c_phone = st.text_input("Contact Phone", key="new_c_phone")
    with ac3:
        c_relation = st.selectbox("Relation",
                                  ["Spouse", "Parent", "Sibling", "Child", "Friend", "Doctor", "Other"],
                                  key="new_c_rel")
    if st.button("➕ Add Contact", use_container_width=True):
        if c_name.strip() and c_phone.strip():
            contacts.append({"name": c_name.strip(), "phone": c_phone.strip(), "relation": c_relation})
            st.session_state.emergency_contacts = contacts
            update_user_fields(email, {"emergency_contacts": contacts})
            st.success(f"Added {c_name}!")
            st.rerun()
        else:
            st.warning("Please fill in name and phone.")

# ── Tab 3: Medical Records ─────────────────────
with tab_records:
    st.markdown("### 🗂️ Medical Records")
    st.caption("Keep diagnoses, reports, and treatment notes together for your next consultation.")
    records = user.get("medical_records", [])
    if records:
        for i, record in enumerate(records):
            with st.expander(f"{record.get('date', 'Undated')} · {record.get('title', 'Medical record')}"):
                st.write(f"**Type:** {record.get('record_type', 'Other')}")
                st.write(record.get("details", "No details provided."))
                if st.button("Delete record", key=f"delete_record_{i}"):
                    db = _load_db()
                    db[email].setdefault("medical_records", []).pop(i)
                    _save_db(db)
                    st.rerun()
    else:
        st.info("No medical records added yet.")

    st.markdown("#### Add a Record")
    rc1, rc2 = st.columns(2)
    record_title = rc1.text_input("Title", placeholder="Annual blood test")
    record_date = rc2.date_input("Date", value=date.today(), key="record_date")
    record_type = st.selectbox("Record type", ["Diagnosis", "Lab report", "Prescription", "Imaging", "Vaccination", "Other"])
    record_details = st.text_area("Details", placeholder="Add the important findings, medicines, or notes.")
    if st.button("Save medical record", type="primary", key="save_record"):
        if not record_title.strip() or not record_details.strip():
            st.warning("Title and details are required.")
        else:
            db = _load_db()
            db[email].setdefault("medical_records", []).append({
                "title": record_title.strip(),
                "date": record_date.isoformat(),
                "record_type": record_type,
                "details": record_details.strip(),
            })
            _save_db(db)
            st.success("Medical record saved.")
            st.rerun()

# ── Tab 4: Family Profiles ─────────────────────
with tab_family:
    st.markdown("### 👨‍👩‍👧 Family Profiles")
    st.caption("Store separate basic health information for people you care for.")
    family = user.get("family_profiles", [])
    if family:
        for i, member in enumerate(family):
            with st.container(border=True):
                fc1, fc2, fc3 = st.columns([2, 1.2, 2.5])
                fc1.write(f"**{member.get('name', 'Family member')}**\n\n{member.get('relation', 'Other')}")
                fc2.write(f"Age: {member.get('age', '—')}\n\nBlood: {member.get('blood_type', 'Unknown')}")
                fc3.write(f"Allergies: {member.get('allergies', 'None')}\n\nConditions: {member.get('conditions', 'None')}")
                if st.button("Remove", key=f"remove_family_{i}"):
                    db = _load_db()
                    db[email].setdefault("family_profiles", []).pop(i)
                    _save_db(db)
                    st.rerun()
    else:
        st.info("No family profiles added yet.")

    st.markdown("#### Add Family Member")
    fc1, fc2, fc3 = st.columns(3)
    family_name = fc1.text_input("Name", key="family_name")
    family_relation = fc2.selectbox("Relation", ["Child", "Parent", "Spouse", "Sibling", "Other"], key="family_relation")
    family_age = fc3.number_input("Age", min_value=0, max_value=120, value=30, key="family_age")
    fc4, fc5 = st.columns(2)
    family_blood = fc4.selectbox("Blood type", ["Unknown"] + list(BLOOD_TYPES), key="family_blood")
    family_allergies = fc5.text_input("Allergies", key="family_allergies")
    family_conditions = st.text_input("Conditions", key="family_conditions")
    if st.button("Save family profile", type="primary", key="save_family"):
        if not family_name.strip():
            st.warning("Name is required.")
        else:
            db = _load_db()
            db[email].setdefault("family_profiles", []).append({
                "name": family_name.strip(), "relation": family_relation,
                "age": family_age, "blood_type": family_blood,
                "allergies": family_allergies.strip(), "conditions": family_conditions.strip(),
            })
            _save_db(db)
            st.success("Family profile saved.")
            st.rerun()

# ── Tab 5: Saved Hospitals ─────────────────────
with tab_saved:
    st.markdown("### 💾 Saved Hospitals")
    saved = st.session_state.get("saved_hospitals", [])
    if not saved:
        st.info("No hospitals saved yet. Go to **Find Hospitals** and click 💾 to save.")
    else:
        for i, h in enumerate(saved):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"""
                <div class="h-card">
                  <p class="h-name">🏥 {h['name']}</p>
                  <p class="h-detail">📍 {h.get('distance_km', '?')} km · {h.get('address', '')}</p>
                  <p class="h-detail">📞 {h.get('phone', 'N/A')}</p>
                </div>""", unsafe_allow_html=True)
            with col2:
                if st.button("🗑️ Remove", key=f"rm_hosp_{i}"):
                    saved.pop(i)
                    st.session_state.saved_hospitals = saved
                    update_user_fields(email, {"saved_hospitals": saved})
                    st.rerun()

# ── Tab 4: Medical ID Card ─────────────────────
with tab_id:
    st.markdown("### 🪪 Medical ID Card")
    ec1 = st.session_state.emergency_contacts[0] if st.session_state.emergency_contacts else None
    ec_str = f"{ec1['name']} ({ec1['relation']}): {ec1['phone']}" if ec1 else "Not set"

    st.markdown(f"""
    <div style="max-width:450px;margin:auto;background:linear-gradient(135deg,#1a237e,#283593);
                color:white;border-radius:16px;padding:24px;box-shadow:0 8px 32px rgba(0,0,0,0.3);">
      <div style="text-align:center;border-bottom:1px solid rgba(255,255,255,0.3);padding-bottom:12px;margin-bottom:16px;">
        <div style="font-size:36px;">🏥</div>
        <h3 style="margin:0;color:white;">MEDICAL ID CARD</h3>
        <p style="margin:0;font-size:12px;color:#90caf9;">Emergency Medical Information</p>
      </div>
      <table style="width:100%;color:white;font-size:14px;">
        <tr><td style="padding:6px;color:#90caf9;">👤 Name</td><td style="padding:6px;"><b>{user.get('name','—')}</b></td></tr>
        <tr><td style="padding:6px;color:#90caf9;">🩸 Blood Type</td><td style="padding:6px;"><b style="color:#ef5350;">{user.get('blood_type','Unknown')}</b></td></tr>
        <tr><td style="padding:6px;color:#90caf9;">⚠️ Allergies</td><td style="padding:6px;">{user.get('allergies','None')}</td></tr>
        <tr><td style="padding:6px;color:#90caf9;">🏥 Conditions</td><td style="padding:6px;">{user.get('conditions','None')}</td></tr>
        <tr><td style="padding:6px;color:#90caf9;">📞 Emergency</td><td style="padding:6px;">{ec_str}</td></tr>
        <tr><td style="padding:6px;color:#90caf9;">📱 Phone</td><td style="padding:6px;">{user.get('phone','—')}</td></tr>
      </table>
      <div style="text-align:center;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.3);">
        <p style="font-size:11px;color:#90caf9;margin:0;">In case of emergency, please call 112</p>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📥 Export Medical Data")
    c1, c2 = st.columns(2)
    txt_data = f"""MEDICAL ID - {user.get('name','—')}
Blood Type: {user.get('blood_type','Unknown')}
Allergies: {user.get('allergies','None')}
Conditions: {user.get('conditions','None')}
Phone: {user.get('phone','—')}
Emergency Contact: {ec_str}
DOB: {user.get('dob','—')}
Gender: {user.get('gender','—')}
Generated: {date.today().isoformat()}
Emergency Number: 112"""
    c1.download_button("📄 Download TXT", txt_data, "medical_id.txt", "text/plain", use_container_width=True)
    json_data = json.dumps({
        "name": user.get("name"), "blood_type": user.get("blood_type"),
        "allergies": user.get("allergies"), "conditions": user.get("conditions"),
        "phone": user.get("phone"), "dob": user.get("dob"),
        "gender": user.get("gender"), "emergency_contact": ec1,
    }, indent=2)
    c2.download_button("📋 Download JSON", json_data, "medical_id.json", "application/json", use_container_width=True)
