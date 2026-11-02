import streamlit as st
from utils.styles import COMMON_CSS
from utils.theme import render_theme_picker, theme_css
from utils.helpers import EMERGENCY_NUMBERS
from utils.auth import login, register, guest_login, logout, render_user_sidebar, ROLES

st.set_page_config(
    page_title="Emergency Hospital Finder",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────
for k, v in {
    "logged_in": False, "user_email": "", "user_role": "",
    "user_name": "", "user_phone": "", "user_dept": "", "user_hosp": "",
    "user_blood_type": "", "user_conditions": "", "user_allergies": "",
    "is_guest": False, "login_time": "",
    "user_lat": None, "user_lng": None, "location_name": "",
    "emergency_contacts": [], "saved_hospitals": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown(COMMON_CSS, unsafe_allow_html=True)
st.markdown(theme_css(), unsafe_allow_html=True)

# ══════════════════════════════════════════════
#   ROLE-BASED NAVIGATION (after login)
# ══════════════════════════════════════════════
if st.session_state.logged_in:
    role = st.session_state.user_role

    # Keep role navigation explicit so each role sees only its own workflow.
    patient_pages = [
        st.Page("pages/0_Emergency_Dashboard.py", title="Emergency Dashboard", icon="🚨", default=True),
        st.Page("pages/1_Find_Hospitals.py",  title="Find Hospitals",      icon="🏥"),
        st.Page("pages/8_Consultations.py",   title="Consultations",   icon="💬"),
        st.Page("pages/2_Blood_Bank.py",      title="Blood Bank",      icon="🩸"),
        st.Page("pages/3_Pharmacy.py",        title="Pharmacy",        icon="💊"),
        st.Page("pages/4_First_Aid_Guide.py", title="First Aid Guide", icon="🆘"),
        st.Page("pages/9_Symptom_Checker.py", title="Symptom Checker", icon="🔍"),
        st.Page("pages/5_My_Profile.py",      title="My Profile",      icon="👤"),
    ]
    doctor_pages = [
        st.Page("pages/11_Doctor_Dashboard.py", title="Doctor Dashboard", icon="📊", default=True),
        st.Page("pages/12_Assigned_Patients.py", title="Assigned Patients", icon="👥"),
        st.Page("pages/8_Consultations.py",   title="Consultations",   icon="💬"),
        st.Page("pages/6_Doctor_Panel.py",    title="Doctor Panel",    icon="🩺"),
        st.Page("pages/9_Symptom_Checker.py", title="Symptom Checker", icon="🔍"),
    ]
    admin_pages = [
        st.Page("pages/7_Admin_Panel.py", title="Admin Panel", icon="⚙️", default=True),
    ]

    pages_map = {
        "patient": patient_pages,
        "doctor":  doctor_pages,
        "admin":   admin_pages,
    }
    pages = pages_map.get(role, patient_pages)

    # Sidebar: logo + user badge + nav
    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:14px 0 8px;'>"
            "<span style='font-size:40px;'>🏥</span><br>"
            "<span style='font-size:15px;font-weight:700;color:#fff;'>Hospital Finder</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border-color:#3949ab55;margin:8px 0;'>", unsafe_allow_html=True)

        # User badge
        role_info = ROLES.get(role, {"label": role, "color": "#3949ab"})
        is_guest  = st.session_state.get("is_guest", False)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.12);border-radius:12px;padding:12px 14px;margin-bottom:6px;">
          <div style="font-size:11px;opacity:.7;">Signed in as</div>
          <div style="font-size:15px;font-weight:700;">{st.session_state.user_name}</div>
          <div style="margin-top:4px;">
            <span style="background:{role_info['color']};color:#fff;padding:2px 10px;
                  border-radius:20px;font-size:11px;font-weight:700;">{role_info['label']}</span>
            {"<span style='background:#ff9800;color:#fff;padding:2px 8px;border-radius:20px;font-size:10px;margin-left:4px;'>GUEST</span>" if is_guest else ""}
          </div>
          {('<div style="font-size:11px;opacity:.65;margin-top:3px;">' + st.session_state.user_dept + (' · ' + st.session_state.user_hosp if st.session_state.user_hosp else '') + '</div>') if st.session_state.user_dept else ""}
        </div>""", unsafe_allow_html=True)

        if st.button("🔓 Logout", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()

        st.markdown("<hr style='border-color:#3949ab55;margin:8px 0;'>", unsafe_allow_html=True)

        # Emergency numbers mini strip
        st.markdown("<p style='font-size:10px;font-weight:700;letter-spacing:1px;color:#90caf9;text-transform:uppercase;margin:4px 0 8px;'>🆘 Emergency</p>", unsafe_allow_html=True)
        for icon, lbl, num in EMERGENCY_NUMBERS[:5]:
            st.markdown(f"<div style='display:flex;justify-content:space-between;background:rgba(255,255,255,.10);border-radius:6px;padding:5px 10px;margin-bottom:4px;'>"
                        f"<span style='font-size:12px;'>{icon} {lbl}</span>"
                        f"<b style='color:#ffcc80;font-size:13px;'>{num}</b></div>",
                        unsafe_allow_html=True)

        st.session_state._theme_picker_rendered = False
        render_theme_picker()

    # Run navigation — this renders the selected page
    pg = st.navigation(pages, position="sidebar")
    pg.run()
    st.stop()

# ══════════════════════════════════════════════
#   LOGIN PAGE  (not logged in)
# ══════════════════════════════════════════════
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] {
      background: linear-gradient(135deg,#0d1b6e 0%,#1a237e 40%,#283593 70%,#1565c0 100%) !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  [data-testid="stSidebar"] { display:none !important; }
  footer, #MainMenu { visibility:hidden; }

  .login-wrap {
      background: rgba(255,255,255,0.97);
      border-radius: 24px; padding: 36px 34px 28px;
      box-shadow: 0 24px 80px rgba(0,0,0,.35);
      max-width: 480px; margin: 0 auto;
  }
  .app-logo { text-align:center; margin-bottom:20px; }
  .app-logo .ico { font-size:64px; line-height:1; }
  .app-logo h1 { font-size:22px; font-weight:800; color:#1a237e; margin:10px 0 4px; }
  .app-logo p  { color:#888; font-size:13px; margin:0; }

  .sos-strip {
      background: linear-gradient(90deg,#b71c1c,#e53935);
      color:#fff; border-radius:10px; padding:10px 16px;
      text-align:center; font-size:13px; font-weight:700;
      margin-bottom:20px; box-shadow:0 4px 16px rgba(229,57,53,.4);
  }
  .demo-box {
      background:#f5f7ff; border:1px solid #c5cae9;
      border-radius:12px; padding:13px 15px; margin-top:14px;
  }
  .d-row { display:flex; justify-content:space-between; align-items:center;
            margin-bottom:5px; font-size:12px; }
  .d-cred { color:#1a237e; font-weight:700; font-family:monospace; font-size:12px; }
  .r-pill { display:inline-block; padding:3px 10px; border-radius:20px;
             font-size:11px; font-weight:700; }
  .chip { display:inline-block; background:#e8eaf6; color:#283593;
          border-radius:20px; padding:4px 12px; font-size:12px; font-weight:600; margin:3px; }
  .chip.no { background:#ffebee; color:#c62828; text-decoration:line-through; }
  .en-row { display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-top:10px; }
  .en-box { background:#fff; border:1px solid #e53935; border-radius:10px;
             padding:6px 12px; text-align:center; min-width:78px; }
  .en-box .n { font-size:16px; font-weight:800; color:#b71c1c; }
  .en-box .l { font-size:10px; color:#888; }
</style>
""", unsafe_allow_html=True)

# Top SOS strip
st.markdown("""
<div class="sos-strip">
  ⚠️ LIFE-THREATENING EMERGENCY — CALL NOW:
  🆘 <b>112</b> &nbsp;│&nbsp; 🚑 <b>102</b> &nbsp;│&nbsp; 👮 <b>100</b> &nbsp;│&nbsp; 🚒 <b>101</b>
</div>""", unsafe_allow_html=True)

# Centered login card
_, mid, _ = st.columns([1, 2.2, 1])
with mid:
    st.markdown("""
    <div class="app-logo">
      <div class="ico">🏥</div>
      <h1>Emergency Hospital Finder</h1>
      <p>Hospitals · Blood Banks · Pharmacies · First Aid — instantly</p>
    </div>""", unsafe_allow_html=True)

    tab_login, tab_signup, tab_guest = st.tabs(["🔐 Login", "📝 Sign Up", "🕶️ Guest"])

    # ── LOGIN ─────────────────────────────────
    with tab_login:
        email_in = st.text_input("📧 Email", placeholder="you@example.com", key="li_e")
        pw_in    = st.text_input("🔑 Password", type="password", key="li_p")

        if st.button("🔐 Login", use_container_width=True, type="primary", key="btn_li"):
            if not email_in.strip() or not pw_in:
                st.error("Enter your email and password.")
            else:
                ok, msg = login(email_in.strip(), pw_in)
                if ok:
                    st.success(f"✅ Welcome, {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("""
        <div class="demo-box">
          <b style="color:#1a237e;font-size:13px;">🧪 Demo Credentials</b>
          <div class="d-row" style="margin-top:8px;">
            <span class="r-pill" style="background:#ffebee;color:#c62828;">🔴 Admin</span>
            <span class="d-cred">admin@emergency.com</span>
            <span class="d-cred">Admin@123</span>
          </div>
          <div class="d-row">
            <span class="r-pill" style="background:#e3f2fd;color:#1565c0;">🔵 Doctor</span>
            <span class="d-cred">doctor@emergency.com</span>
            <span class="d-cred">Doctor@123</span>
          </div>
          <div class="d-row">
            <span class="r-pill" style="background:#e8f5e9;color:#2e7d32;">🟢 Patient</span>
            <span class="d-cred">patient@emergency.com</span>
            <span class="d-cred">Patient@123</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── SIGN UP ───────────────────────────────
    with tab_signup:
        s_name  = st.text_input("👤 Full Name",  placeholder="Rahul Sharma",       key="su_n")
        s_email = st.text_input("📧 Email",       placeholder="you@example.com",    key="su_e")
        s_phone = st.text_input("📞 Phone",       placeholder="+91 XXXXX XXXXX",   key="su_ph")
        s_role  = st.selectbox("🎭 Register As",
                                ["patient","doctor"],
                                format_func=lambda x:
                                    "🟢 Patient — find hospitals & emergencies"
                                    if x=="patient" else
                                    "🔵 Doctor / Medical Staff — + hospital management",
                                key="su_r")
        if s_role == "doctor":
            s_dept = st.text_input("🏥 Dept, Hospital",
                                   placeholder="e.g. Emergency Medicine, AIIMS Delhi",
                                   key="su_d")
        else:
            s_dept = ""
        s_pw  = st.text_input("🔑 Password",         type="password", key="su_pw")
        s_cpw = st.text_input("🔑 Confirm Password", type="password", key="su_cp")

        # Access preview
        if s_role == "patient":
            st.markdown("<div style='margin-top:8px;'><b style='font-size:12px;'>✅ You will get access to:</b><br>"
                        "<span class='chip'>🏥 Hospitals</span><span class='chip'>🩸 Blood Bank</span>"
                        "<span class='chip'>💊 Pharmacy</span><span class='chip'>🆘 First Aid</span>"
                        "<span class='chip'>👤 Profile</span>"
                        "<span class='chip no'>🩺 Doctor Panel</span><span class='chip no'>⚙️ Admin</span>"
                        "</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top:8px;'><b style='font-size:12px;'>✅ You will get access to:</b><br>"
                        "<span class='chip'>🏥 Hospitals</span><span class='chip'>🩸 Blood Bank</span>"
                        "<span class='chip'>💊 Pharmacy</span><span class='chip'>🆘 First Aid</span>"
                        "<span class='chip'>👤 Profile</span><span class='chip'>🩺 Doctor Panel</span>"
                        "<span class='chip no'>⚙️ Admin</span>"
                        "</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Create Account", use_container_width=True, type="primary", key="btn_su"):
            if s_pw != s_cpw:
                st.error("❌ Passwords do not match.")
            elif not all([s_name.strip(), s_email.strip(), s_pw]):
                st.error("❌ Name, email, and password are required.")
            else:
                dept = s_dept.split(",")[0].strip() if s_dept and "," in s_dept else s_dept.strip()
                hosp = s_dept.split(",")[1].strip() if s_dept and "," in s_dept else ""
                ok, msg = register(s_email, s_pw, s_name,
                                   role=s_role, phone=s_phone,
                                   department=dept, hospital=hosp)
                st.success(msg + " ← Switch to Login tab.") if ok else st.error(msg)

    # ── GUEST ─────────────────────────────────
    with tab_guest:
        st.markdown("""
        <div style="background:#fff8e1;border:1px solid #ffc107;border-radius:12px;padding:14px 16px;margin-bottom:12px;">
          <b style="color:#e65100;">🕶️ Guest Access — No Sign-up Needed</b><br>
          <span style="font-size:13px;color:#555;">Patient-level access. Data is session-only.</span>
        </div>
        <b style="font-size:12px;">Guest gets access to:</b>
        <div style="margin-top:6px;">
          <span class="chip">🏥 Hospitals</span><span class="chip">🩸 Blood Bank</span>
          <span class="chip">💊 Pharmacy</span><span class="chip">🆘 First Aid</span>
          <span class="chip">👤 Profile</span>
          <span class="chip no">🩺 Doctor Panel</span><span class="chip no">⚙️ Admin Panel</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Continue as Guest", use_container_width=True, type="primary", key="btn_gu"):
            guest_login()
            st.rerun()

# Emergency numbers at bottom
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<p style='text-align:center;color:#ddd;font-size:13px;font-weight:700;'>📞 Emergency Numbers — No Login Required</p>",
            unsafe_allow_html=True)
en_cols = st.columns(4)
for i, (icon, lbl, num) in enumerate(EMERGENCY_NUMBERS[:8]):
    with en_cols[i % 4]:
        st.markdown(f"""
        <div class="en-box" style="margin-bottom:8px;">
          <div>{icon}</div>
          <div class="n">{num}</div>
          <div class="l">{lbl}</div>
        </div>""", unsafe_allow_html=True)
