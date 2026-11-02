import streamlit as st
from utils.styles import COMMON_CSS
from utils.auth import check_auth

st.markdown(COMMON_CSS, unsafe_allow_html=True)
check_auth(required_roles=["patient"])

st.markdown("""
<div class="app-header">
  <div style="font-size:50px;">🆘</div>
  <div><h1>First Aid Guide</h1>
       <p>Emergency response protocols · Step-by-step instructions · Save lives</p></div>
</div>""", unsafe_allow_html=True)

# ── Project Features ────────────────────────────
st.markdown("---")
st.markdown("### 🌟 Project Features")

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("""
    <div class='welcome-card'>
      <div class='icon'>🏥</div>
      <h4>Find Hospitals</h4>
      <ul style='text-align:left;font-size:13px;'>
        <li>Live OSM data — no API key</li>
        <li>Auto-detect or manual location</li>
        <li>Map / List / Table views</li>
        <li>One-click Google Maps directions</li>
        <li>One-click phone call</li>
        <li>Save hospitals to profile</li>
        <li>Filter by Hospital / Clinic</li>
        <li>Sort by distance or name</li>
      </ul>
    </div>""", unsafe_allow_html=True)
with f2:
    st.markdown("""
    <div class='welcome-card'>
      <div class='icon'>💬</div>
      <h4>Doctor Consultations</h4>
      <ul style='text-align:left;font-size:13px;'>
        <li>Patient ↔ Doctor messaging</li>
        <li>Doctor assignment system</li>
        <li>Real-time chat interface</li>
        <li>Prescription sending (highlighted)</li>
        <li>Admin can view all chats</li>
        <li>Change doctor anytime</li>
        <li>Message history persistence</li>
        <li>Role-based access control</li>
      </ul>
    </div>""", unsafe_allow_html=True)
with f3:
    st.markdown("""
    <div class='welcome-card'>
      <div class='icon'>💊</div>
      <h4>Pharmacy Interaction</h4>
      <ul style='text-align:left;font-size:13px;'>
        <li>Find 24×7 pharmacies nearby</li>
        <li>Interactive map with markers</li>
        <li>Order / prescription requests</li>
        <li>Pharmacy auto-response system</li>
        <li>Chat history per pharmacy</li>
        <li>Download pharmacy data as CSV</li>
        <li>Filter by 24×7 availability</li>
        <li>Call pharmacy directly</li>
      </ul>
    </div>""", unsafe_allow_html=True)

f4, f5, f6 = st.columns(3)
with f4:
    st.markdown("""
    <div class='welcome-card'>
      <div class='icon'>🩸</div>
      <h4>Blood Bank</h4>
      <ul style='text-align:left;font-size:13px;'>
        <li>Find blood banks nearby</li>
        <li>Blood type compatibility chart</li>
        <li>Simulated availability data</li>
        <li>Filter by needed blood type</li>
        <li>Map and list views</li>
        <li>Directions + call buttons</li>
      </ul>
    </div>""", unsafe_allow_html=True)
with f5:
    st.markdown("""
    <div class='welcome-card'>
      <div class='icon'>🔐</div>
      <h4>Role-Based Access</h4>
      <ul style='text-align:left;font-size:13px;'>
        <li>Login / Sign Up / Guest access</li>
        <li>Admin, Doctor, Patient roles</li>
        <li>Role-specific page visibility</li>
        <li>Admin panel for user management</li>
        <li>Doctor panel with capacity data</li>
        <li>Secure password hashing (SHA-256)</li>
      </ul>
    </div>""", unsafe_allow_html=True)
with f6:
    st.markdown("""
    <div class='welcome-card'>
      <div class='icon'>👤</div>
      <h4>Profile & Emergency</h4>
      <ul style='text-align:left;font-size:13px;'>
        <li>Medical profile management</li>
        <li>Emergency contact storage</li>
        <li>Saved hospitals list</li>
        <li>Emergency numbers (112, 102, etc.)</li>
        <li>India-specific helplines</li>
        <li>First aid guide protocols</li>
      </ul>
    </div>""", unsafe_allow_html=True)

# ── First Aid Protocols ────────────────────────
st.markdown("---")
st.markdown("### 🆘 Emergency First Aid Protocols")

tabs = st.tabs(["❤️ CPR", "🧠 Stroke", "🩸 Bleeding", "🔥 Burns", "🦴 Fractures",
                "😵 Choking", "☠️ Poisoning", "⚡ Seizure", "🫁 Asthma", "💉 Diabetic", "🌊 Drowning"])

with tabs[0]:
    st.markdown("### ❤️ CPR (Cardiopulmonary Resuscitation)")
    st.markdown("""
    **When to use:** Person is unresponsive and not breathing normally.
    
    1. **Check** — Tap shoulders, shout "Are you OK?"
    2. **Call 112** — Ask someone to call emergency services
    3. **Position** — Place person on firm, flat surface
    4. **Hands** — Place heel of one hand on center of chest, other hand on top
    5. **Compress** — Push hard and fast: **100–120 compressions/min**, **2 inches deep**
    6. **Breathe** — Tilt head back, lift chin, give 2 rescue breaths every 30 compressions
    7. **Continue** — Don't stop until help arrives or person responds
    
    > ⚠️ **Do NOT:** Stop CPR to check for pulse repeatedly. Do NOT compress on ribs or stomach.
    
    📞 **Emergency:** 112 | Ambulance: 102
    """)

with tabs[1]:
    st.markdown("### 🧠 Stroke — Act F.A.S.T.")
    st.markdown("""
    **F.A.S.T. Method:**
    
    - **F — Face:** Ask the person to smile. Does one side droop?
    - **A — Arms:** Ask them to raise both arms. Does one drift down?
    - **S — Speech:** Ask them to repeat a simple phrase. Is it slurred?
    - **T — Time:** If any of these signs, call **112** IMMEDIATELY
    
    1. Note the exact time symptoms began
    2. Keep the person calm and lying down
    3. Do NOT give food, water, or medicine
    4. Do NOT let them drive
    
    > ⚠️ Every minute matters — brain cells die rapidly during a stroke.
    
    📞 **Emergency:** 112
    """)

with tabs[2]:
    st.markdown("### 🩸 Severe Bleeding")
    st.markdown("""
    1. **Protect yourself** — Wear gloves if available
    2. **Apply pressure** — Press firmly with a clean cloth on the wound
    3. **Elevate** — Raise the injured limb above heart level
    4. **Maintain pressure** — Do NOT remove the cloth; add more if soaked through
    5. **Tourniquet** — Only if bleeding is life-threatening and cannot be controlled
    6. **Call 112** — If bleeding doesn't stop in 10 minutes
    
    > ⚠️ **Do NOT:** Remove embedded objects. Do NOT use a tourniquet unless trained.
    
    📞 **Emergency:** 112 | Ambulance: 102
    """)

with tabs[3]:
    st.markdown("### 🔥 Burns")
    st.markdown("""
    1. **Cool** — Hold burn under cool running water for **10–20 minutes**
    2. **Remove** — Gently remove jewelry/clothing near the burn (not stuck items)
    3. **Cover** — Loosely with sterile, non-fluffy dressing or cling film
    4. **Pain** — Paracetamol or ibuprofen for minor burns
    5. **Seek help** — For burns larger than palm, on face/hands/joints, or blistering
    
    > ⚠️ **Do NOT:** Apply ice, butter, toothpaste, or ointment to severe burns. Do NOT burst blisters.
    
    📞 **Emergency:** 112
    """)

with tabs[4]:
    st.markdown("### 🦴 Fractures")
    st.markdown("""
    1. **Immobilize** — Keep the injured area completely still
    2. **Support** — Use padding (towels, pillows) around the injury
    3. **Ice** — Apply ice pack wrapped in cloth for 20 min on, 20 min off
    4. **Splint** — Only if trained; otherwise wait for paramedics
    5. **Elevate** — If possible, keep injured limb elevated
    
    > ⚠️ **Do NOT:** Try to realign the bone. Do NOT move the person if spine injury is suspected.
    
    📞 **Ambulance:** 102
    """)

with tabs[5]:
    st.markdown("### 😵 Choking (Heimlich Maneuver)")
    st.markdown("""
    **For Adults:**
    1. Stand behind the person, wrap arms around their waist
    2. Make a fist with one hand, place it above the navel
    3. Grasp with other hand and deliver **quick upward thrusts**
    4. Repeat until object is expelled or person becomes unconscious
    
    **For Infants (< 1 year):**
    1. Hold face-down on your forearm
    2. Give **5 back blows** between shoulder blades
    3. Turn over, give **5 chest thrusts** with 2 fingers
    
    > ⚠️ **Do NOT:** Perform blind finger sweeps. Call 112 if choking persists.
    """)

with tabs[6]:
    st.markdown("### ☠️ Poisoning")
    st.markdown("""
    1. **Identify** — What was swallowed, inhaled, or touched?
    2. **Call** — Poison Control: **1800-11-6117** or Emergency: **112**
    3. **Do NOT induce vomiting** — Unless specifically told by poison control
    4. **If inhaled** — Move to fresh air immediately
    5. **If on skin** — Remove contaminated clothing, wash with water for 15 min
    6. **Save** — Keep the container/substance for medical team
    
    > ⚠️ **Do NOT:** Give anything by mouth unless directed. Do NOT wait for symptoms.
    
    📞 **Poison Control:** 1800-11-6117
    """)

with tabs[7]:
    st.markdown("### ⚡ Seizure")
    st.markdown("""
    1. **Clear** — Move objects away from the person
    2. **Protect** — Place something soft under their head
    3. **Time** — Note when the seizure starts
    4. **Recovery position** — Turn on their side after the seizure stops
    5. **Stay** — Remain with them until fully conscious
    
    > ⚠️ **Do NOT:** Restrain them. Do NOT put anything in their mouth. Call 112 if seizure lasts > 5 minutes.
    
    📞 **Emergency:** 112
    """)

with tabs[8]:
    st.markdown("### 🫁 Asthma Attack")
    st.markdown("""
    1. **Sit upright** — Help them sit up straight
    2. **Inhaler** — Help them use their reliever inhaler (usually blue)
    3. **Dose** — 1 puff every 30–60 seconds, up to 10 puffs
    4. **Calm** — Keep them calm, encourage slow breathing
    5. **Call 112** — If no inhaler, no improvement, or getting worse
    
    > ⚠️ **Do NOT:** Make them lie down. Do NOT leave them alone.
    
    📞 **Emergency:** 112
    """)

with tabs[9]:
    st.markdown("### 💉 Diabetic Emergency")
    st.markdown("""
    **Low Blood Sugar (Hypoglycemia) Signs:** Shaking, sweating, confusion, irritability
    
    1. **Give sugar** — Glucose tablets, fruit juice, or regular soda
    2. **Wait 15 min** — Then recheck
    3. **Follow up** — Give a snack with protein (crackers + cheese)
    4. **Call 112** — If person is unconscious or not improving
    
    **High Blood Sugar (Hyperglycemia) Signs:** Excessive thirst, frequent urination, fruity breath
    
    1. **Help take insulin** — If they have it prescribed
    2. **Give water** — Keep them hydrated
    3. **Call 112** — If confused, vomiting, or breathing rapidly
    
    > ⚠️ **Do NOT:** Give insulin to someone who is unconscious.
    """)

with tabs[10]:
    st.markdown("### 🌊 Drowning")
    st.markdown("""
    1. **Call for help** — Shout for a lifeguard, call **112**
    2. **Reach or throw** — Use a pole, rope, or flotation device. Do NOT jump in unless trained
    3. **Remove from water** — Once safe, lay on back on a firm surface
    4. **Check breathing** — If not breathing, begin CPR immediately
    5. **Recovery position** — If breathing, place on their side
    6. **Keep warm** — Cover with blankets, remove wet clothing
    
    > ⚠️ **Do NOT:** Attempt a water rescue unless you are a trained swimmer. 
    
    📞 **Emergency:** 112 | Coast Guard: 1554
    """)
