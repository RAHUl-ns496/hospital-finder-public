import streamlit as st
from utils.styles import COMMON_CSS
from utils.auth import check_auth

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["patient", "doctor"])

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">🔍</div>
  <div><h1>Symptom Checker</h1>
       <p>Rule-based triage · Find the right specialist · Know when to seek emergency care</p></div>
</div>""", unsafe_allow_html=True)

st.markdown("<div class='sos-banner'>⚠️ This is NOT a medical diagnosis. Always consult a qualified healthcare professional.</div>",
            unsafe_allow_html=True)

ALL_SYMPTOMS = [
    "Fever", "Headache", "Chest Pain", "Shortness of Breath", "Abdominal Pain",
    "Nausea/Vomiting", "Dizziness", "Cough", "Sore Throat", "Body Ache",
    "Fatigue", "Rash/Skin Issues", "Joint Pain", "Back Pain", "Eye Pain/Redness",
    "Ear Pain", "Toothache", "Anxiety/Stress", "Insomnia", "Diarrhea",
    "Constipation", "Urinary Issues", "Bleeding", "Numbness/Tingling", "Swelling"
]

SYMPTOM_SPECIALIST = {
    "Chest Pain": "Cardiologist", "Shortness of Breath": "Pulmonologist",
    "Headache": "Neurologist", "Dizziness": "Neurologist", "Numbness/Tingling": "Neurologist",
    "Rash/Skin Issues": "Dermatologist", "Joint Pain": "Orthopedic",
    "Back Pain": "Orthopedic", "Eye Pain/Redness": "Ophthalmologist",
    "Ear Pain": "ENT Specialist", "Sore Throat": "ENT Specialist",
    "Toothache": "Dentist", "Abdominal Pain": "Gastroenterologist",
    "Nausea/Vomiting": "Gastroenterologist", "Diarrhea": "Gastroenterologist",
    "Constipation": "Gastroenterologist", "Urinary Issues": "Urologist",
    "Anxiety/Stress": "Psychiatrist", "Insomnia": "Psychiatrist",
    "Fever": "General Physician", "Cough": "General Physician",
    "Body Ache": "General Physician", "Fatigue": "General Physician",
    "Bleeding": "Emergency Medicine", "Swelling": "General Physician",
}

# ── Input Section ──────────────────────────────
st.markdown("### 📋 Enter Your Symptoms")

symptoms = st.multiselect("Select all symptoms you are experiencing:", ALL_SYMPTOMS)

c1, c2, c3 = st.columns(3)
with c1:
    duration = st.selectbox("Duration", ["Just started", "Few hours", "1-2 days", "3-7 days", "More than a week"])
with c2:
    severity = st.slider("Severity (1=Mild, 10=Severe)", 1, 10, 3)
with c3:
    age = st.number_input("Age", min_value=1, max_value=120, value=30)

gender = st.selectbox("Gender", ["Male", "Female", "Other"])

# ── Analysis ───────────────────────────────────
if st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True):
    if not symptoms:
        st.warning("Please select at least one symptom.")
        st.stop()

    # Rule-based triage
    emergency_combos = [
        {"Chest Pain", "Shortness of Breath"},
        {"Bleeding", "Dizziness"},
        {"Chest Pain", "Numbness/Tingling"},
    ]
    emergency_single = {"Bleeding", "Chest Pain"}

    is_emergency = False
    is_urgent = False
    is_moderate = False

    sym_set = set(symptoms)

    # Check emergency
    if severity >= 9:
        is_emergency = True
    for combo in emergency_combos:
        if combo.issubset(sym_set):
            is_emergency = True
    if severity >= 8 and sym_set & emergency_single:
        is_emergency = True

    # Check urgent
    if not is_emergency:
        if severity >= 7:
            is_urgent = True
        if "Fever" in sym_set and duration in ["3-7 days", "More than a week"]:
            is_urgent = True
        if len(symptoms) >= 4 and severity >= 5:
            is_urgent = True

    # Check moderate
    if not is_emergency and not is_urgent:
        if len(symptoms) >= 2 or severity >= 4 or duration in ["3-7 days", "More than a week"]:
            is_moderate = True

    # Determine level
    if is_emergency:
        level, color, icon, bg = "🚨 EMERGENCY", "#c62828", "🚑", "#ffebee"
        action = "Call **112** immediately or go to the nearest Emergency Room."
    elif is_urgent:
        level, color, icon, bg = "⚠️ URGENT", "#e65100", "🏥", "#fff3e0"
        action = "Visit a doctor or hospital **within 24 hours**. Do not delay."
    elif is_moderate:
        level, color, icon, bg = "🟡 MODERATE", "#f9a825", "👨‍⚕️", "#fffde7"
        action = "Schedule a doctor's appointment **within 2-3 days**."
    else:
        level, color, icon, bg = "🟢 MILD", "#2e7d32", "💊", "#e8f5e9"
        action = "Monitor symptoms at home. Visit a doctor if symptoms persist or worsen."

    st.markdown("---")
    st.markdown("### 📊 Analysis Results")

    # Triage Card
    st.markdown(f"""
    <div style="background:{bg};border-left:6px solid {color};border-radius:12px;padding:20px;margin:16px 0;">
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="font-size:40px;">{icon}</span>
        <div>
          <h2 style="margin:0;color:{color};">{level}</h2>
          <p style="margin:4px 0 0 0;font-size:16px;">{action}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Recommended Specialists
    specialists = set()
    for s in symptoms:
        if s in SYMPTOM_SPECIALIST:
            specialists.add(SYMPTOM_SPECIALIST[s])
    if not specialists:
        specialists.add("General Physician")

    st.markdown("#### 👨‍⚕️ Recommended Specialists")
    spec_cols = st.columns(min(len(specialists), 4))
    for i, spec in enumerate(sorted(specialists)):
        with spec_cols[i % len(spec_cols)]:
            st.markdown(f"""
            <div style="background:white;border:2px solid {color};border-radius:10px;padding:14px;text-align:center;">
              <div style="font-size:24px;">🩺</div>
              <b>{spec}</b>
            </div>""", unsafe_allow_html=True)

    # What to do next
    st.markdown("#### 📝 What To Do Next")
    steps = []
    if is_emergency:
        steps = ["Call 112 or go to ER immediately", "Do not drive yourself", "Bring a list of current medications",
                 "Have someone accompany you", "Stay calm and monitor symptoms"]
    elif is_urgent:
        steps = ["Book an appointment with a specialist today", "Keep a symptom diary with timestamps",
                 "Take over-the-counter relief if safe", "Avoid strenuous activities", "Stay hydrated and rest"]
    elif is_moderate:
        steps = ["Schedule a doctor visit within 2-3 days", "Monitor if symptoms worsen",
                 "Rest and stay hydrated", "Track your temperature if feverish", "Avoid self-medication for unknown conditions"]
    else:
        steps = ["Rest at home and monitor symptoms", "Stay hydrated — drink water and warm fluids",
                 "Use OTC medicines for mild relief", "Visit a doctor if symptoms persist beyond 3 days",
                 "Maintain good hygiene to prevent spread"]

    for i, step in enumerate(steps, 1):
        st.markdown(f"**{i}.** {step}")

    st.markdown(f"""
    <div style="background:#fff3e0;border-radius:8px;padding:12px;margin-top:16px;border:1px solid #ffe0b2;">
      ⚠️ <b>Disclaimer:</b> This symptom checker uses basic rules and is NOT a substitute for professional medical advice.
      Always consult a qualified healthcare professional for proper diagnosis and treatment.
    </div>""", unsafe_allow_html=True)

# ── Common Conditions Reference ────────────────
st.markdown("---")
st.markdown("### 📚 Common Conditions Reference")

with st.expander("🤧 Common Cold"):
    st.markdown("""
    **Symptoms:** Runny nose, sneezing, sore throat, mild cough, low-grade fever
    
    **Home Remedies:** Rest, warm fluids, honey + ginger tea, steam inhalation, gargling with salt water
    
    **See a doctor if:** Fever > 102°F, symptoms last > 10 days, difficulty breathing, severe sinus pain
    """)

with st.expander("🤒 Flu (Influenza)"):
    st.markdown("""
    **Symptoms:** High fever, severe body aches, extreme fatigue, dry cough, headache
    
    **Home Remedies:** Complete rest, plenty of fluids, paracetamol for fever, isolation to prevent spread
    
    **See a doctor if:** Difficulty breathing, chest pain, persistent vomiting, symptoms worsen after improving
    """)

with st.expander("🧠 Migraine"):
    st.markdown("""
    **Symptoms:** Intense throbbing headache (usually one side), nausea, light/sound sensitivity, visual aura
    
    **Home Remedies:** Dark quiet room, cold compress on forehead, caffeine in small amounts, adequate sleep
    
    **See a doctor if:** Worst headache of your life, headache with fever/stiff neck, vision changes, weakness
    """)

with st.expander("🍔 Food Poisoning"):
    st.markdown("""
    **Symptoms:** Nausea, vomiting, diarrhea, stomach cramps, fever, within hours of eating
    
    **Home Remedies:** Sip clear fluids (ORS), BRAT diet (bananas, rice, applesauce, toast), rest
    
    **See a doctor if:** Blood in stool, fever > 101.5°F, dehydration signs, symptoms > 3 days
    """)

with st.expander("🚽 Urinary Tract Infection (UTI)"):
    st.markdown("""
    **Symptoms:** Burning during urination, frequent urge, cloudy/strong-smelling urine, pelvic pain
    
    **Home Remedies:** Drink plenty of water, cranberry juice (unsweetened), avoid caffeine/alcohol
    
    **See a doctor if:** Blood in urine, back/side pain, fever, symptoms persist > 2 days (antibiotics needed)
    """)

with st.expander("🤮 Allergic Reaction"):
    st.markdown("""
    **Symptoms:** Hives, itching, swelling, sneezing, watery eyes. Severe: difficulty breathing, throat swelling
    
    **Home Remedies:** Antihistamines (cetirizine), cold compress, avoid known allergens
    
    **See a doctor if:** Difficulty breathing, swelling of face/throat, dizziness — **Call 112 for anaphylaxis**
    """)
