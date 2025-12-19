import streamlit as st
import json
from langchain_community.chat_models import ChatOllama
from ner_module import extract_medical_entities
from knowledge_graph import MedicalKnowledgeGraph
from local import StandaloneDoctorFinder

# -------------------------------
# STEP 1: Setup (Ollama)
# -------------------------------
llm = ChatOllama(
    model="llama3",
    temperature=0.7
)

kg = MedicalKnowledgeGraph()
doctor_finder = StandaloneDoctorFinder()

# -------------------------------
# STEP 2: Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="MediCare AI", page_icon="🩺", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
.chat-bubble {
    border-radius: 16px;
    padding: 12px 16px;
    margin: 8px 0;
    line-height: 1.5;
    font-size: 1rem;
}
.assistant {
    background-color: #f1f5f9;
    color: #111;
}
.user {
    background-color: #d1fae5;
    text-align: right;
    color: #111;
}
.doctor-card {
    color: black;
    border-radius: 14px;
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 12px 16px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.doctor-name {
    font-weight: bold;
    color: #111827;
    font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🩺 MediCare AI — Smart Health Triage Assistant")
st.caption("Describe your symptoms and I’ll help you understand what might be happening.")

# -------------------------------
# STEP 3: Session State
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hello! I'm MediCare AI. What symptoms are you experiencing today?"}
    ]
if "conversation" not in st.session_state:
    st.session_state.conversation = ""
if "symptoms" not in st.session_state:
    st.session_state.symptoms = []
if "done" not in st.session_state:
    st.session_state.done = False
if "specialties" not in st.session_state:
    st.session_state.specialties = []

# -------------------------------
# STEP 4: Display Chat
# -------------------------------
for msg in st.session_state.chat_history:
    role = msg["role"]
    color_class = "assistant" if role == "assistant" else "user"
    st.markdown(f"<div class='chat-bubble {color_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# -------------------------------
# STEP 5: User Input
# -------------------------------
if not st.session_state.done:
    user_input = st.chat_input("Describe your symptoms...")
else:
    user_input = None

if user_input and not st.session_state.done:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.conversation += f"Patient: {user_input}\n"

    with st.spinner("🤖 Analyzing your symptoms..."):
        entities = extract_medical_entities(user_input)
        st.session_state.symptoms = list(set(st.session_state.symptoms + entities.get("symptoms", [])))

    # Knowledge Graph lookup
    possible_specialties = kg.get_specialty_for_symptoms(st.session_state.symptoms)
    st.session_state.specialties = possible_specialties or ["General Practitioner"]

    followup_prompt = f"""
    You are a medical triage assistant.
    Conversation so far:
    {st.session_state.conversation}

    Detected symptoms: {st.session_state.symptoms}.
    Knowledge graph suggests specialties: {possible_specialties}.

    Ask ONE short follow-up question to clarify the condition.
    If enough information, reply exactly with "DONE".
    """

    with st.spinner("💭 Thinking..."):
        next_step = llm.invoke(followup_prompt).content.strip()

    if next_step.upper() == "DONE":
        st.session_state.done = True
        summary_prompt = f"""
        You are an empathetic AI triage assistant.
        Based on this conversation:
        {st.session_state.conversation}

        Detected symptoms: {st.session_state.symptoms}.
        Provide a short, clear summary:
        - Mention possible conditions (not diagnosis)
        - Recommend specialist
        - Include disclaimer
        """
        with st.spinner("🩺 Preparing summary..."):
            summary = llm.invoke(summary_prompt).content
        st.session_state.chat_history.append({"role": "assistant", "content": summary})
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": next_step})
        st.session_state.conversation += f"Bot: {next_step}\n"

    st.rerun()

# -------------------------------
# STEP 6: Doctor Finder
# -------------------------------
if st.session_state.done:
    st.divider()
    st.subheader("📍 Find Nearby Specialists")

    location = st.text_input("Enter your city or area:")
    if location:
        with st.spinner("🔍 Searching nearby clinics..."):
            try:
                nearby = doctor_finder.find_doctors(st.session_state.specialties[0], location)
                if nearby:
                    st.success(f"🏥 Nearby {st.session_state.specialties[0]} Specialists:")
                    for doc in nearby:
                        st.markdown(f"""
                        <div class="doctor-card">
                            <div class="doctor-name">👨‍⚕️ {doc['name']}</div>
                            <div>{doc['specialty']}</div>
                            <div>🏥 {doc['address']}</div>
                            <div>⭐ {doc['rating']} / 5 &nbsp; | &nbsp; 📞 {doc['phone']}</div>
                            <div>🕒 {doc['availability']} &nbsp; | &nbsp; 📏 {doc['distance']}</div>
                            <div><i>{doc['source']}</i></div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No real facilities found — showing mock data.")
            except Exception as e:
                st.error(f"Error fetching doctors: {e}")

        st.info("🩹 This is not a diagnosis. Please consult a licensed doctor for medical advice.")

# -------------------------------
# STEP 7: Restart Button
# -------------------------------
st.divider()
if st.button("🔄 Start New Consultation"):
    for key in ["chat_history", "conversation", "symptoms", "done", "specialties"]:
        st.session_state.pop(key, None)
    st.rerun()
