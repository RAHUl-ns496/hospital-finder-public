import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from utils.styles import COMMON_CSS
from utils.helpers import EMERGENCY_NUMBERS
from utils.auth import (check_auth, ROLES,
                         get_all_users, toggle_user_active, change_user_role,
                         delete_user, register)

check_auth(required_roles=["admin"])

st.markdown(COMMON_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.admin-metric { background:#fff;border-radius:12px;padding:16px;text-align:center;
               box-shadow:0 2px 8px rgba(0,0,0,.07);border-top:4px solid; }
.admin-metric .val { font-size:30px;font-weight:800; }
.admin-metric .lbl { font-size:12px;color:#888;margin-top:2px; }
</style>""", unsafe_allow_html=True)

role_info = ROLES.get("admin", {"label":"Admin","color":"#c62828"})
st.markdown(f"""
<div class="app-header">
  <div style="font-size:50px;">⚙️</div>
  <div style="flex:1;">
    <h1>System Admin Panel</h1>
    <p>User management · Role control · System analytics · Account administration</p>
  </div>
  <div style="text-align:right;">
    <div style="font-size:13px;opacity:.75;">Administrator</div>
    <div style="font-size:15px;font-weight:700;">{st.session_state.user_name}</div>
    <span style="background:{role_info['color']};color:#fff;padding:2px 12px;border-radius:20px;font-size:12px;">
      🔴 Admin
    </span>
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="sos-banner">⚙️ Administrator Access · Full System Control · Handle with care</div>""",
unsafe_allow_html=True)

# ── Load users ────────────────────────────────
users_db     = get_all_users()
total_users  = len(users_db)
admins       = sum(1 for u in users_db.values() if u.get("role")=="admin")
doctors      = sum(1 for u in users_db.values() if u.get("role")=="doctor")
patients     = sum(1 for u in users_db.values() if u.get("role")=="patient")
active_users = sum(1 for u in users_db.values() if u.get("active",True))
inactive     = total_users - active_users

# ── Metrics ───────────────────────────────────
mc1,mc2,mc3,mc4,mc5,mc6 = st.columns(6)
for col,(val,lbl,color) in zip([mc1,mc2,mc3,mc4,mc5,mc6],[
    (total_users,  "Total Users",  "#1a237e"),
    (active_users, "Active",       "#2e7d32"),
    (inactive,     "Inactive",     "#c62828"),
    (admins,       "Admins",       "#b71c1c"),
    (doctors,      "Doctors",      "#1565c0"),
    (patients,     "Patients",     "#2e7d32"),
]):
    with col:
        st.markdown(f"<div class='admin-metric' style='border-top-color:{color};'>"
                    f"<div class='val' style='color:{color};'>{val}</div>"
                    f"<div class='lbl'>{lbl}</div></div>", unsafe_allow_html=True)

st.markdown("---")
tab_users, tab_add, tab_analytics, tab_system = st.tabs(
    ["👥 User Management", "➕ Add User", "📊 Analytics", "⚙️ System Info"])

# ── USER MANAGEMENT ───────────────────────────
with tab_users:
    st.markdown("### 👥 All Registered Users")
    fc1,fc2,fc3 = st.columns(3)
    role_filter   = fc1.selectbox("Filter Role",   ["All","admin","doctor","patient"])
    status_filter = fc2.selectbox("Filter Status", ["All","Active","Inactive"])
    search_user   = fc3.text_input("🔎 Search",    placeholder="Name or email…")

    filtered = {
        email: data for email, data in users_db.items()
        if (role_filter=="All" or data.get("role")==role_filter)
        and (status_filter=="All"
             or (status_filter=="Active"   and data.get("active",True))
             or (status_filter=="Inactive" and not data.get("active",True)))
        and (not search_user or search_user.lower() in email.lower()
             or search_user.lower() in data.get("name","").lower())
    }
    st.caption(f"Showing {len(filtered)} of {total_users} users")

    for email, data in filtered.items():
        role      = data.get("role","patient")
        ri        = ROLES.get(role, {"label":role,"color":"#666"})
        is_active = data.get("active",True)
        is_self   = email == st.session_state.user_email

        uc1,uc2,uc3,uc4,uc5 = st.columns([3,2,1.5,1.2,1])
        with uc1:
            you_badge = ("<span style='background:#ff9800;color:#fff;padding:1px 7px;"
                         "border-radius:10px;font-size:10px;margin-left:6px;'>YOU</span>"
                         if is_self else "")
            st.markdown(f"<div style='background:#fff;border-radius:10px;padding:10px 14px;"
                        f"box-shadow:0 1px 6px rgba(0,0,0,.06);'>"
                        f"<b>{data.get('name','—')}</b>{you_badge}<br>"
                        f"<span style='font-size:12px;color:#888;'>📧 {email}</span><br>"
                        f"<span style='font-size:12px;color:#888;'>📞 {data.get('phone','—')}</span>"
                        f"</div>", unsafe_allow_html=True)
        with uc2:
            dept = data.get("department",""); hosp = data.get("hospital","")
            st.markdown(f"<div style='padding-top:6px;font-size:12px;color:#555;'>"
                        f"{'🏥 '+dept+'<br>' if dept else ''}"
                        f"{'🩺 '+hosp+'<br>' if hosp else ''}"
                        f"📅 {data.get('created_at','—')}</div>", unsafe_allow_html=True)
        with uc3:
            rc = ri["color"]
            st.markdown(f"<div style='padding-top:10px;'>"
                        f"<span style='background:{rc}22;color:{rc};border:1px solid {rc}55;"
                        f"border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700;'>{ri['label']}</span></div>",
                        unsafe_allow_html=True)
        with uc4:
            color = "#2e7d32" if is_active else "#c62828"
            txt   = "✅ Active" if is_active else "❌ Inactive"
            st.markdown(f"<div style='padding-top:12px;font-size:13px;color:{color};font-weight:600;'>{txt}</div>",
                        unsafe_allow_html=True)
        with uc5:
            if not is_self:
                if st.button("🔄",key=f"tog_{email}",help="Toggle active/inactive"):
                    toggle_user_active(email); st.rerun()
                new_role = st.selectbox("",["admin","doctor","patient"],
                                        index=["admin","doctor","patient"].index(role),
                                        key=f"role_{email}", label_visibility="collapsed")
                if new_role != role:
                    change_user_role(email, new_role); st.rerun()
                if st.button("🗑️",key=f"del_{email}",help="Delete user"):
                    if delete_user(email): st.rerun()

# ── ADD USER ──────────────────────────────────
with tab_add:
    st.markdown("### ➕ Create New User Account")
    ac1,ac2 = st.columns(2)
    with ac1:
        an  = st.text_input("👤 Full Name", key="an")
        ae  = st.text_input("📧 Email",     key="ae")
        aph = st.text_input("📞 Phone",     key="aph")
        ar  = st.selectbox("🎭 Role",["patient","doctor","admin"], key="ar",
                           format_func=lambda x:{"patient":"🟢 Patient","doctor":"🔵 Doctor","admin":"🔴 Admin"}[x])
    with ac2:
        ad  = st.text_input("🏥 Department", key="ad", placeholder="e.g. Emergency Medicine")
        ah  = st.text_input("🏥 Hospital",   key="ah", placeholder="e.g. AIIMS Delhi")
        apw = st.text_input("🔑 Password",   type="password", key="apw")
        acp = st.text_input("🔑 Confirm",    type="password", key="acp")

    if st.button("✅ Create User", type="primary", use_container_width=True):
        if apw != acp:                    st.error("Passwords don't match.")
        elif not all([an,ae,apw]):        st.error("Name, email and password required.")
        else:
            ok,msg = register(ae,apw,an,role=ar,phone=aph,department=ad,hospital=ah)
            st.success(msg) if ok else st.error(msg)
            if ok: st.rerun()

# ── ANALYTICS ─────────────────────────────────
with tab_analytics:
    st.markdown("### 📊 Platform Analytics (Simulated)")
    ac1,ac2 = st.columns(2)
    with ac1:
        st.markdown("#### 🎭 Role Distribution")
        role_df = pd.DataFrame({"Role":["Admin","Doctor","Patient"],"Count":[admins,doctors,patients]})
        st.bar_chart(role_df.set_index("Role"))
        st.markdown("#### 📅 Registrations (Simulated)")
        import numpy as np
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug"]
        reg_df = pd.DataFrame({"Month":months,"New Users":np.random.randint(5,30,len(months))})
        st.line_chart(reg_df.set_index("Month"))
    with ac2:
        st.markdown("#### 🔍 Feature Usage (Simulated)")
        feat_df = pd.DataFrame({
            "Feature":["Find Hospitals","Blood Bank","Pharmacy","First Aid","Doctor Panel"],
            "Uses":   [random.randint(200,1000) for _ in range(5)]})
        st.bar_chart(feat_df.set_index("Feature"))
        st.markdown("#### 🌍 Top Cities (Simulated)")
        city_df = pd.DataFrame({
            "City":   ["Delhi","Mumbai","Bangalore","Chennai","Hyderabad","Kolkata"],
            "Searches":[random.randint(100,500) for _ in range(6)]
        }).sort_values("Searches",ascending=False)
        st.dataframe(city_df,use_container_width=True,hide_index=True)

# ── SYSTEM INFO ───────────────────────────────
with tab_system:
    st.markdown("### ⚙️ System Information")
    si1,si2 = st.columns(2)
    with si1:
        import platform, sys
        st.markdown(f"""
| Info | Value |
|------|-------|
| **App Version** | 2.0.0 |
| **Python** | {sys.version.split()[0]} |
| **Platform** | {platform.system()} {platform.release()} |
| **Data Source** | OpenStreetMap (Overpass API) |
| **Auth** | SHA-256 + JSON DB |
| **Total Users** | {total_users} |
| **Server Time** | {datetime.now().strftime("%d %b %Y %H:%M:%S")} |
        """)
    with si2:
        st.markdown("#### 📋 Role Permissions Matrix")
        perm_df = pd.DataFrame({
            "Feature":["Find Hospitals","Blood Bank","Pharmacy","First Aid","My Profile","Doctor Panel","Admin Panel"],
            "Patient":["✅","✅","✅","✅","✅","❌","❌"],
            "Doctor": ["✅","✅","✅","✅","✅","✅","❌"],
            "Admin":  ["✅","✅","✅","✅","✅","✅","✅"],
        })
        st.dataframe(perm_df,use_container_width=True,hide_index=True)

    st.markdown("---")
    with st.expander("⚠️ Danger Zone — Reset User Database"):
        st.warning("Deletes ALL accounts except the default admin. Irreversible!")
        confirm = st.text_input("Type CONFIRM to proceed", key="danger_confirm")
        if st.button("🗑️ Reset Users",type="primary") and confirm=="CONFIRM":
            import hashlib
            from utils.auth import _save_db
            default = {"admin@emergency.com":{
                "password_hash":hashlib.sha256(b"Admin@123").hexdigest(),
                "name":"System Administrator","role":"admin",
                "phone":"","department":"Administration","hospital":"",
                "created_at":datetime.now().strftime("%Y-%m-%d"),"active":True}}
            _save_db(default)
            st.success("✅ Database reset. Only admin remains.")
            st.rerun()
