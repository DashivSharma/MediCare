import streamlit as st
from agent_workflow_v3 import run_medical_step
from local import StandaloneDoctorFinder
from email_send import send_email

# -------------------------------
# INIT
# -------------------------------
doctor_finder = StandaloneDoctorFinder()

st.set_page_config(
    page_title="MediCare AI",
    page_icon="🩺",
    layout="centered"
)

# -------------------------------
# SESSION STATE
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "👋 Hello! I'm MediCare AI. What symptoms are you experiencing?"
        }
    ]

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "conversation": "",
        "symptoms": [],
        "question_count": 0,
        "done": False
    }

if "specialties" not in st.session_state:
    st.session_state.specialties = []

if "booked_doctor" not in st.session_state:
    st.session_state.booked_doctor = None

# -------------------------------
# UI HEADER
# -------------------------------
st.title("🩺 MediCare AI — Smart Health Triage Assistant")
st.caption("Describe your symptoms and I’ll guide you to the right specialist.")

# -------------------------------
# CHAT DISPLAY
# -------------------------------
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# -------------------------------
# CHAT INPUT
# -------------------------------
if not st.session_state.agent_state["done"]:
    user_input = st.chat_input("Describe your symptoms...")
else:
    user_input = None

if user_input and not st.session_state.agent_state["done"]:
    # show user message
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    # CALL AGENT WORKFLOW (THIS IS THE KEY CHANGE)
    result = run_medical_step(
        user_input,
        st.session_state.agent_state
    )

    # update agent state
    st.session_state.agent_state = result["state"]

    # agent response
    if result["type"] == "QUESTION":
        st.session_state.chat_history.append(
            {"role": "assistant", "content": result["message"]}
        )

    elif result["type"] == "DONE":
        st.session_state.chat_history.append(
            {"role": "assistant", "content": result["summary"]}
        )
        st.session_state.specialties = [result["specialist"]]

    st.rerun()

# -------------------------------
# DOCTOR FINDER
# -------------------------------
if st.session_state.agent_state["done"]:
    st.divider()
    st.subheader("📍 Find Nearby Specialists")

    location = st.text_input("Enter your city or locality")

    if location:
        with st.spinner("🔍 Searching nearby doctors..."):
            nearby = doctor_finder.find_doctors(
                st.session_state.specialties[0],
                location
            )

        if nearby:
            st.success(f"🏥 {st.session_state.specialties[0]} near you:")

            for i, doc in enumerate(nearby):
                clicked = st.button(
                    f"👨‍⚕️ {doc['name']} — Book Appointment",
                    key=f"book_{i}",
                    use_container_width=True
                )

                st.markdown(
                    f"""
                    **{doc['name']}**  
                    {doc['specialty']}  
                    🏥 {doc['address']}  
                    ⭐ {doc['rating']} | 📞 {doc['phone']}  
                    🕒 {doc['availability']} | 📏 {doc['distance']}
                    """,
                    unsafe_allow_html=True
                )

                if clicked:
                    try:
                        # 🔹 Call send_email (LLM + SMTP happens INSIDE this)
                        send_email(
                            summary=st.session_state.chat_history[-1]["content"],  # agent summary
                            doctor_email=doc["email"],
                            doctor_name=doc["name"],
                            patient_location=location
                        )

                        st.session_state.booked_doctor = doc
                        st.toast("📧 Appointment request sent to clinic!", icon="✅")

                    except Exception as e:
                        st.error(f"❌ Failed to send appointment email: {e}")

        else:
            st.warning("⚠️ No doctors found nearby.")

# -------------------------------
# CONFIRMATION POPUP
# -------------------------------
if st.session_state.booked_doctor:
    st.success(
        f"✅ Appointment successfully booked with "
        f"**{st.session_state.booked_doctor['name']}**.\n\n"
        "📧 Confirmation email has been sent."
    )

# -------------------------------
# RESET
# -------------------------------
st.divider()
if st.button("🔄 Start New Consultation"):
    for key in [
        "chat_history",
        "agent_state",
        "specialties",
        "booked_doctor"
    ]:
        st.session_state.pop(key, None)
    st.rerun()
