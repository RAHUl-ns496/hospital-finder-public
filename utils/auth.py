import streamlit as st
import hashlib
from datetime import datetime
from utils.mongo import users_collection
from utils.helpers import valid_email, valid_phone

# ── Role hierarchy ───────────────────────────
ROLES = {
    "admin":   {"label": "🔴 Admin",    "color": "#c62828", "badge": "b-red"},
    "doctor":  {"label": "🔵 Doctor",   "color": "#1565c0", "badge": "b-blue"},
    "patient": {"label": "🟢 Patient",  "color": "#2e7d32", "badge": "b-green"},
}

ROLE_PERMISSIONS = {
    "admin":   ["admin_panel"],
    "doctor":  ["consultations","doctor_panel","symptom_checker"],
    "patient": ["emergency_dashboard","find_hospitals","consultations","pharmacy",
                 "blood_bank","first_aid","symptom_checker","profile"],
}

# ── DB helpers ────────────────────────────────
def _load_db():
    return {
        user["email"]: {key: value for key, value in user.items() if key != "_id" and key != "email"}
        for user in users_collection().find({})
    }

def _save_db(db):
    collection = users_collection()
    collection.delete_many({})
    collection.insert_many([dict(user, email=email) for email, user in db.items()]) if db else None

def update_user_fields(email, fields):
    if not fields:
        return False
    result = users_collection().update_one({"email": email}, {"$set": fields})
    return result.matched_count > 0

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Auth actions ─────────────────────────────
def login(email, password):
    db = _load_db()
    email = email.strip().lower()
    user = db.get(email)
    if not user:
        return False, "❌ Email not found."
    if not user.get("active", True):
        return False, "🚫 Account is deactivated. Contact admin."
    if user["password_hash"] != _hash(password):
        return False, "❌ Incorrect password."
    # Set session
    st.session_state.logged_in   = True
    st.session_state.user_email  = email
    st.session_state.user_role   = user["role"]
    st.session_state.user_name   = user["name"]
    st.session_state.user_phone  = user.get("phone","")
    st.session_state.user_dept   = user.get("department","")
    st.session_state.user_hosp   = user.get("hospital","")
    st.session_state.user_blood_type = user.get("blood_type","")
    st.session_state.user_conditions = user.get("conditions","")
    st.session_state.user_allergies  = user.get("allergies","")
    st.session_state.emergency_contacts = user.get("emergency_contacts", [])
    st.session_state.saved_hospitals = user.get("saved_hospitals", [])
    st.session_state.login_time  = datetime.now().strftime("%d %b %Y %H:%M")
    return True, "success"

def register(email, password, name, role="patient", **extra):
    db = _load_db()
    email = email.strip().lower()
    if not valid_email(email):
        return False, "⚠️ Enter a valid email address."
    if email in db:
        return False, "⚠️ Email already registered."
    if len(password) < 8:
        return False, "⚠️ Password must be at least 8 characters."
    if not name.strip():
        return False, "⚠️ Name is required."
    if not valid_phone(extra.get("phone", "")):
        return False, "⚠️ Enter a valid phone number."
    if role not in ROLES:
        return False, "⚠️ Invalid account role."
    db[email] = {
        "password_hash": _hash(password),
        "name": name.strip(),
        "role": role,
        "phone": extra.get("phone",""),
        "department": extra.get("department",""),
        "hospital": extra.get("hospital",""),
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "active": True,
    }
    _save_db(db)
    return True, "✅ Account created! Please log in."

def guest_login():
    st.session_state.logged_in   = True
    st.session_state.user_email  = "guest@emergency.com"
    st.session_state.user_role   = "patient"
    st.session_state.user_name   = "Guest User"
    st.session_state.user_phone  = ""
    st.session_state.user_dept   = ""
    st.session_state.user_hosp   = ""
    st.session_state.user_blood_type = ""
    st.session_state.user_conditions = ""
    st.session_state.user_allergies  = ""
    st.session_state.login_time  = datetime.now().strftime("%d %b %Y %H:%M")
    st.session_state.is_guest    = True

def logout():
    for key in ["logged_in","user_email","user_role","user_name","user_phone",
                "user_dept","user_hosp","user_blood_type","user_conditions",
                "user_allergies","login_time","is_guest","hospitals","pharmacies",
                "blood_banks","h_searched","ph_searched","bb_searched",
                "emergency_contacts","saved_hospitals"]:
        st.session_state.pop(key, None)

def change_password(email, old_pw, new_pw):
    db = _load_db()
    user = db.get(email)
    if not user or user["password_hash"] != _hash(old_pw):
        return False, "❌ Current password is incorrect."
    if len(new_pw) < 6:
        return False, "⚠️ New password must be at least 6 characters."
    db[email]["password_hash"] = _hash(new_pw)
    _save_db(db)
    return True, "✅ Password updated successfully."

# ── Admin: user management ────────────────────
def get_all_users():
    db = _load_db()
    return db

def toggle_user_active(email):
    db = _load_db()
    if email in db:
        db[email]["active"] = not db[email].get("active", True)
        _save_db(db)
        return db[email]["active"]
    return None

def change_user_role(email, new_role):
    db = _load_db()
    if email in db and new_role in ROLES:
        db[email]["role"] = new_role
        _save_db(db)
        return True
    return False

def delete_user(email):
    db = _load_db()
    if email in db:
        del db[email]
        _save_db(db)
        return True
    return False

# ── Guards ────────────────────────────────────
def check_auth(required_roles=None):
    """Call at top of each page. required_roles=None means any logged-in user."""
    if not st.session_state.get("logged_in"):
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:64px;">🔐</div>
          <h2 style="color:#1a237e;">Authentication Required</h2>
          <p style="color:#666;">Please log in to access this page.</p>
          <a href="/" style="background:#1a237e;color:#fff;padding:12px 28px;
             border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;">
            ← Go to Login
          </a>
        </div>""", unsafe_allow_html=True)
        st.stop()

    if required_roles and st.session_state.get("user_role") not in required_roles:
        role = st.session_state.get("user_role","unknown")
        role_info = ROLES.get(role, {"label":role,"color":"#666"})
        st.markdown(f"""
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:64px;">🚫</div>
          <h2 style="color:#c62828;">Access Denied</h2>
          <p style="color:#666;">Your role (<b>{role_info['label']}</b>) does not have permission to view this page.</p>
          <a href="/" style="background:#1a237e;color:#fff;padding:12px 28px;
             border-radius:10px;text-decoration:none;font-weight:700;font-size:15px;">
            ← Back to Dashboard
          </a>
        </div>""", unsafe_allow_html=True)
        st.stop()

# ── Sidebar user badge ────────────────────────
def render_user_sidebar():
    role = st.session_state.get("user_role","patient")
    role_info = ROLES.get(role, {"label":role,"color":"#3949ab"})
    is_guest = st.session_state.get("is_guest", False)
    st.markdown(f"""
    <div style="background:rgba(255,255,255,.12);border-radius:12px;padding:12px 14px;margin-bottom:10px;">
      <div style="font-size:13px;opacity:.75;">Logged in as</div>
      <div style="font-size:15px;font-weight:700;">{st.session_state.get('user_name','User')}</div>
      <div style="font-size:12px;margin-top:3px;">
        <span style="background:{role_info['color']};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;">
          {role_info['label']}
        </span>
        {"&nbsp;<span style='background:#ff9800;color:#fff;padding:2px 8px;border-radius:20px;font-size:10px;'>GUEST</span>" if is_guest else ""}
      </div>
      <div style="font-size:11px;opacity:.65;margin-top:4px;">
        {st.session_state.get('user_dept','')}
        {(' · ' + st.session_state.get('user_hosp','')) if st.session_state.get('user_hosp') else ''}
      </div>
    </div>""", unsafe_allow_html=True)
    if st.button("🔓 Logout", use_container_width=True):
        logout()
        st.rerun()
