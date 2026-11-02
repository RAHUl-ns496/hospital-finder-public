import streamlit as st
from utils.auth import render_user_sidebar, ROLES

# Pages each role can access (file paths relative to app root)
ROLE_PAGES = {
    "patient": [
        st.Page("pages/0_Emergency_Dashboard.py", title="Emergency Dashboard", icon="🚨"),
        st.Page("pages/1_Find_Hospitals.py",  title="Find Hospitals",  icon="🏥"),
        st.Page("pages/2_Blood_Bank.py",      title="Blood Bank",      icon="🩸"),
        st.Page("pages/3_Pharmacy.py",        title="Pharmacy",        icon="💊"),
        st.Page("pages/4_First_Aid_Guide.py", title="First Aid Guide", icon="🆘"),
        st.Page("pages/5_My_Profile.py",      title="My Profile",      icon="👤"),
    ],
    "doctor": [
        st.Page("pages/11_Doctor_Dashboard.py", title="Doctor Dashboard", icon="📊"),
        st.Page("pages/12_Assigned_Patients.py", title="Assigned Patients", icon="👥"),
        st.Page("pages/8_Consultations.py",   title="Consultations",   icon="💬"),
        st.Page("pages/6_Doctor_Panel.py",    title="Doctor Panel",    icon="🩺"),
        st.Page("pages/9_Symptom_Checker.py", title="Symptom Checker", icon="🔍"),
    ],
    "admin": [
        st.Page("pages/7_Admin_Panel.py",     title="Admin Panel",     icon="⚙️"),
    ],
}

def run_navigation():
    """
    Build role-based navigation and run it.
    Call this at the top of every page (after auth check).
    Returns the current page object.
    """
    role = st.session_state.get("user_role", "patient")
    pages = ROLE_PAGES.get(role, ROLE_PAGES["patient"])

    # Sidebar top: user badge + logout
    with st.sidebar:
        st.markdown(
            "<div style='text-align:center;padding:10px 0 4px;'>"
            "<span style='font-size:36px;'>🏥</span><br>"
            "<span style='font-size:13px;font-weight:700;color:#fff;'>Hospital Finder</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr style='border-color:#3949ab55;margin:8px 0;'>", unsafe_allow_html=True)
        render_user_sidebar()
        st.markdown("<hr style='border-color:#3949ab55;margin:8px 0;'>", unsafe_allow_html=True)

    pg = st.navigation(pages, position="sidebar")
    return pg
