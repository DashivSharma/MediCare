from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.chat_models import ChatOllama
from ner_module import extract_medical_entities
from knowledge_graph import MedicalKnowledgeGraph
from local import StandaloneDoctorFinder
import json
# -------------------------------
# STEP 1: Setup Ollama LLM
# -------------------------------
llm = ChatOllama(
    model="llama3",
    temperature=0.3   # LOWER temp = more reliable medical questioning
)

kg = MedicalKnowledgeGraph()
doctor_finder = StandaloneDoctorFinder()

# -------------------------------
# STEP 2: Tools
# -------------------------------
ner_tool = Tool(
    name="Medical Entity Extractor",
    func=extract_medical_entities,
    description="Extracts medical entities like symptoms, diseases, and medications from the patient's text."
)

kg_tool = Tool(
    name="Medical Knowledge Graph Query",
    func=kg.get_specialty_for_symptoms,
    description="Finds recommended medical specialties for given symptoms."
)

tools = [ner_tool, kg_tool]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)
# -------------------------------
# STEP 3: Chat Logic
# -------------------------------
def run_medical_chatbot():
    print("🩺 Welcome to MediCare AI — your virtual health assistant.")
    print("Let's start your triage process.\n")

    conversation_history = ""
    patient_input = input("🤒 Please describe your symptoms:\n> ")

    # --- Initial entity extraction ---
    entities = extract_medical_entities(patient_input)
    print("\n📊 Extracted Entities:")
    print(json.dumps(entities, indent=2))

    symptoms = entities.get("symptoms", [])
    if not symptoms:
        print("\n⚠️ No clear symptoms detected. Please try describing again.")
        return

    conversation_history += f"Patient: {patient_input}\n"

    MAX_QUESTIONS = 2
    question_count = 0

    while question_count < MAX_QUESTIONS:
        possible_specialties = kg.get_specialty_for_symptoms(symptoms)

        followup_prompt = f"""
    You are a medical triage assistant.

    Conversation so far:
    {conversation_history}

    Detected symptoms: {symptoms}
    Suggested specialties: {possible_specialties}

    Ask ONE short follow-up question.
    If you are confident enough to proceed, reply ONLY with:
    DONE
    """
        response = llm.invoke(followup_prompt).content.strip()

        # ✅ LLM decides it is done
        if response.upper() == "DONE":
            print("\n✅ LLM indicates enough information collected.")
            break

        print(f"\n🩻 {response}")
        user_ans = input("> ")

        conversation_history += f"Q: {response}\nA: {user_ans}\n"

        # Update symptoms
        entities = extract_medical_entities(user_ans)
        symptoms = list(set(symptoms + entities.get("symptoms", [])))

        question_count += 1

    # 🔴 HARD SAFETY STOP
    if question_count == MAX_QUESTIONS:
        print("\n⚠️ Maximum number of follow-up questions reached. Proceeding with available information.")

    # -------------------------------
    # STEP X: Decide Final Specialist
    # -------------------------------

    specialties = kg.get_specialty_for_symptoms(symptoms)

    if specialties:
        final_specialist = specialties[0]
    else:
        # KG failed → ask LLM ONCE
        llm_specialist_prompt = f"""
    You are a medical triage assistant.

    Based ONLY on these symptoms:
    {symptoms}

    Suggest the SINGLE most appropriate medical specialist.
    Reply with ONLY the specialist name.
    No explanations.
    """
        final_specialist = llm.invoke(llm_specialist_prompt).content.strip()

        if not final_specialist:
            final_specialist = "General Practitioner"

    # --- Summary ---
    summary_prompt = f"""
You are an empathetic AI triage assistant.

Conversation:
{conversation_history}

Detected symptoms: {symptoms}

IMPORTANT:
- The recommended specialist is: {final_specialist}
- You MUST NOT suggest any other specialist.

Provide a short non-diagnostic summary.
Explain why this specialist is appropriate.
Include a gentle disclaimer.
"""

    summary = llm.invoke(summary_prompt).content
    print("\n🤖 MediCare AI Summary:\n")
    print(summary)

    # --- Doctor Finder ---
    location = input("\n📍 Enter your city/locality:\n> ")
    specialties = [final_specialist]

    print(f"\n🧠 Suggested Specialist: {specialties[0]}")
    try:
        nearby = doctor_finder.find_doctors(specialties[0], location)
        if nearby:
            print("\n🏥 Nearby facilities:\n")
            for i, doc in enumerate(nearby, start=1):
                print(f"{i}. {doc}")
        else:
            print("⚠️ No nearby doctors found.")
    except Exception as e:
        print(f"⚠️ Error: {e}")

    print("\n🙏 This is not a medical diagnosis. Please consult a healthcare professional.")

def run_medical_step(user_input, state):
    """
    This wraps the existing agent logic for Streamlit.
    """

    conversation_history = state.get("conversation", "")
    symptoms = state.get("symptoms", [])
    question_count = state.get("question_count", 0)
    MAX_QUESTIONS = 2

    # ---- extract entities ----
    entities = extract_medical_entities(user_input)
    symptoms = list(set(symptoms + entities.get("symptoms", [])))

    conversation_history += f"Patient: {user_input}\n"

    # ---- ask follow-up ----
    followup_prompt = f"""
You are a medical triage assistant.

Conversation so far:
{conversation_history}

Detected symptoms: {symptoms}

Ask ONE short follow-up question.
If confident enough, reply ONLY with DONE.
"""

    response = llm.invoke(followup_prompt).content.strip()

    # ---- stop condition ----
    if response.upper() == "DONE" or question_count >= MAX_QUESTIONS:
        specialties = kg.get_specialty_for_symptoms(symptoms)
        final_specialist = specialties[0] if specialties else "General Practitioner"

        summary_prompt = f"""
You are an empathetic AI triage assistant.

Conversation:
{conversation_history}

Symptoms: {symptoms}
Recommended specialist: {final_specialist}

Provide a short non-diagnostic summary with disclaimer.
"""

        summary = llm.invoke(summary_prompt).content

        return {
            "type": "DONE",
            "summary": summary,
            "specialist": final_specialist,
            "state": {
                "conversation": conversation_history,
                "symptoms": symptoms,
                "question_count": question_count,
                "done": True
            }
        }

    # ---- ask question ----
    question_count += 1
    conversation_history += f"Bot: {response}\n"

    return {
        "type": "QUESTION",
        "message": response,
        "state": {
            "conversation": conversation_history,
            "symptoms": symptoms,
            "question_count": question_count,
            "done": False
        }
    }


# -------------------------------
# STEP 4: Run
# -------------------------------
if __name__ == "__main__":
    run_medical_chatbot()
    kg.close()
