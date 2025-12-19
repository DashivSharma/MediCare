# from langchain.agents import initialize_agent, AgentType, Tool
# # from langchain_google_genai import ChatGoogleGenerativeAI
# from ner_module import extract_medical_entities
# from knowledge_graph import MedicalKnowledgeGraph
# from local import StandaloneDoctorFinder
# # from dotenv import load_dotenv
# # import os
# import re, json
# from langchain_community.chat_models import ChatOllama


# # -------------------------------
# # STEP 1: Environment & Setup
# # -------------------------------
# # # load_dotenv()
# # api_key = os.getenv("GOOGLE_API_KEY")
# # if not api_key:
# #     raise ValueError("GOOGLE_API_KEY not found in .env file.")

# llm = ChatOllama(
#     model="llama3",
#     temperature=0.7
# )


# kg = MedicalKnowledgeGraph()
# doctor_finder = StandaloneDoctorFinder()

# # -------------------------------
# # STEP 2: Tools
# # -------------------------------
# ner_tool = Tool(
#     name="Medical Entity Extractor",
#     func=extract_medical_entities,
#     description="Extracts medical entities like symptoms, diseases, and medications from the patient's text."
# )

# kg_tool = Tool(
#     name="Medical Knowledge Graph Query",
#     func=kg.get_specialty_for_symptoms,
#     description="Finds recommended medical specialties for given symptoms."
# )

# tools = [ner_tool, kg_tool]
# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     handle_parsing_errors=True
# )

# # def compute_confidence(symptoms, specialties, questions_asked):
# #         confidence = 0

# #         # Symptom coverage (max 60)
# #         confidence += min(len(symptoms) * 15, 60)

# #         # Specialty certainty (max 30)
# #         if len(specialties) == 1:
# #             confidence += 30
# #         elif len(specialties) == 2:
# #             confidence += 20
# #         else:
# #             confidence += 10

# #         # Question efficiency (max 10)
# #         confidence += min(questions_asked * 5, 10)

# #         return min(confidence, 100)
# def get_llm_confidence(llm, conversation, entities, specialties):
#     prompt = f"""
# You are evaluating how confident a medical triage system should be.

# Your job is NOT to diagnose.
# Your job is to estimate how confident we are that:
# - Enough information has been collected
# - Further questions will add little value

# Consider:
# - Confirmations (yes/no answers)
# - Symptoms ruled out
# - Consistency of answers
# - Specialty narrowing or stability

# Return ONLY valid JSON:
# {{
#   "confidence": <integer 0-100>
# }}

# Rules:
# - Confidence MUST increase when uncertainty decreases
# - Even YES/NO confirmations increase confidence
# - Reach 100 when further questioning is unnecessary
# - Do NOT explain
# - Do NOT include text outside JSON

# Conversation:
# {conversation}

# Entities so far:
# {json.dumps(entities, indent=2)}

# Candidate specialties:
# {specialties}
# """

#     response = llm.invoke(prompt).content.strip()
#     match = re.search(r"\{.*\}", response, re.DOTALL)
#     if not match:
#         return 0

#     try:
#         return int(json.loads(match.group(0)).get("confidence", 0))
#     except:
#         return 0
   
# def merge_entities(old_entities, new_entities):
#     merged = {}

#     for key in ["symptoms", "diseases", "medication"]:
#         old_set = set(old_entities.get(key, []))
#         new_set = set(new_entities.get(key, []))
#         merged[key] = list(old_set.union(new_set))

#     return merged


# # -------------------------------
# # STEP 3: Chat Logic
# # -------------------------------
# # def run_medical_chatbot():
# #     entities = {
# #     "symptoms": [],
# #     "diseases": [],
# #     "medication": []
# #     }

# #     confidence_score = 0


# #     print("🩺 Welcome to MediCare AI — your virtual health assistant.")
# #     print("Let's start your triage process.\n")

# #     conversation_history = ""
# #     patient_input = input("🤒 Please describe your symptoms:\n> ")

# #     # --- Initial entity extraction ---
# #     entities = extract_medical_entities(patient_input)
# #     print("\n📊 Extracted Entities:")
# #     print(json.dumps(entities, indent=2))

# #     symptoms = entities.get("symptoms", [])
# #     if not symptoms:
# #         print("\n⚠️ No clear symptoms detected. Please try describing again.")
# #         return

# #     conversation_history += f"Patient: {patient_input}\n"

# #     # --- Interactive follow-up loop ---
# #     while True:
# #         possible_specialties = kg.get_specialty_for_symptoms(symptoms)

# #         followup_prompt = f"""
# #         You are a medical triage assistant.
# #         Conversation so far:
# #         {conversation_history}

# #         Detected symptoms: {symptoms}.
# #         Knowledge graph suggests specialties: {possible_specialties}.
        
# #         Ask ONE relevant short follow-up question to clarify the patient's condition.
# #         You have a limit of 5 questions but try to get it as soon as possible.
# #         If you have enough information to proceed, reply exactly with "DONE".
# #         """
# #         next_q = llm.invoke(followup_prompt).content.strip()

# #         if next_q.upper() == "DONE":
# #             break

# #         print(f"\n🩻 {next_q}")
# #         user_ans = input("> ")

# #         # Add to history
# #         conversation_history += f"Q: {next_q}\nA: {user_ans}\n"

# #         # --- Extract entities after each answer ---
# #         entities = extract_medical_entities(user_ans)
# #         print("\n📊 Updated Entities:")
# #         print(json.dumps(entities, indent=2))

# #         # Merge new entities with previous ones
# #         symptoms = list(set(symptoms + entities.get("symptoms", [])))

# #         questions_asked += 1

# #         confidence_score = compute_confidence(
# #             symptoms,
# #             possible_specialties,
# #             questions_asked
# #         )

# #         print(f"\n📈 Confidence Score: {confidence_score}%")

# #         if confidence_score >= 100:
# #             print("\n✅ Sufficient information gathered.")
# #             break


# #     # --- Generate summary ---
# #     # summary_prompt = f"""
# #     # You are an empathetic AI triage assistant.
# #     # Based on this conversation:
# #     # {conversation_history}

# #     # Detected symptoms: {symptoms}.
# #     # Provide a short non-diagnostic summary:
# #     # - Mention likely conditions (not a diagnosis)
# #     # - Recommend relevant medical specialists
# #     # - Include a gentle disclaimer
# #     # """
# #     # summary = llm.invoke(summary_prompt).content
# #     # print("\n🤖 MediCare AI Summary:\n")
# #     # print(summary)
# #     # --- Generate summary using Knowledge Graph ---
# #     specialties = kg.get_specialty_for_symptoms(symptoms)
# #     if not specialties:
# #         specialties = ["General Practitioner"]

# #     summary_prompt = f"""
# #     You are an empathetic AI triage assistant.
# #     Based on this conversation:
# #     {conversation_history}

# #     Detected symptoms: {symptoms}.
# #     The recommended medical specialties (from the knowledge graph) are: {specialties}.

# #     Now write a concise, non-diagnostic summary including:
# #     - A short empathetic summary of the condition.
# #     - Mention possible (not confirmed) causes or conditions based on the symptoms.
# #     - Explicitly list the recommended specialties from above.
# #     - Add a gentle disclaimer about consulting a doctor.
# #     """
# #     summary = llm.invoke(summary_prompt).content
# #     print(f"\n🎯 Final Confidence Score: {confidence_score}%")
# #     print("\n🤖 MediCare AI Summary (Knowledge Graph Based):\n")
# #     print(summary)

# #     # --- Find nearby doctors ---
# #     location = input("\n📍 Enter your city/locality to find nearby specialists:\n> ")

# #     print(f"\n🧠 Suggested Specialist: {specialties[0]}")
# #     try:
# #         nearby = doctor_finder.find_doctors(specialties[0], location)
# #         if nearby:
# #             print("\n🏥 Nearby facilities:\n")
# #             for i, doc in enumerate(nearby, start=1):
# #                 print(f"{i}. {doc}")
# #         else:
# #             print("⚠️ No nearby doctors found at the moment.")
# #     except Exception as e:
# #         print(f"⚠️ Error fetching nearby doctors: {e}")

# #     print("\n🙏 Take care! This is not a medical diagnosis — please consult a healthcare professional.")

# # def run_medical_chatbot():
# #     print("🩺 Welcome to MediCare AI — your virtual health assistant.")
# #     print("Let's start your triage process.\n")

# #     conversation_history = ""
# #     confidence_score = 0

# #     # Persistent entities across the session
# #     entities = {
# #         "symptoms": [],
# #         "diseases": [],
# #         "medication": []
# #     }

# #     # ---------------- Initial Input ----------------
# #     patient_input = input("🤒 Please describe your symptoms:\n> ")
# #     conversation_history += f"Patient: {patient_input}\n"

# #     # Initial entity extraction (MERGED)
# #     new_entities = extract_medical_entities(patient_input)
# #     entities = merge_entities(entities, new_entities)

# #     print("\n📊 Extracted Entities:")
# #     print(json.dumps(entities, indent=2))

# #     if not entities["symptoms"]:
# #         print("\n⚠️ No clear symptoms detected. Please try describing again.")
# #         return

# #     # ---------------- Interactive Loop ----------------
# #     while True:
# #         symptoms = entities["symptoms"]
# #         possible_specialties = kg.get_specialty_for_symptoms(symptoms)

# #         followup_prompt = f"""
# # You are a medical triage assistant.

# # Conversation so far:
# # {conversation_history}

# # Extracted medical entities:
# # {json.dumps(entities, indent=2)}

# # Knowledge graph suggests specialties:
# # {possible_specialties}

# # Ask ONE short, relevant follow-up question.
# # If no further clarification is needed, reply exactly with "DONE".
# # """

# #         next_q = llm.invoke(followup_prompt).content.strip()

# #         if next_q.upper() == "DONE":
# #             print("\n✅ No more clarification needed.")
# #             break

# #         print(f"\n🩻 {next_q}")
# #         user_ans = input("> ")
# #         if not user_ans.strip():
# #             print("⚠️ Empty response detected. Skipping entity extraction.")
# #             continue

# #         conversation_history += f"Q: {next_q}\nA: {user_ans}\n"

# #         # --------- Entity update (MERGED) ---------
# #         new_entities = extract_medical_entities(user_ans)
# #         entities = merge_entities(entities, new_entities)

# #         print("\n📊 Updated Entities:")
# #         print(json.dumps(entities, indent=2))

# #         # --------- Confidence update (LLM-driven) ---------
# #         confidence_score = get_llm_confidence(
# #             llm,
# #             conversation_history,
# #             entities,
# #             possible_specialties
# #         )

# #         print(f"\n📈 Confidence Score: {confidence_score}%")

# #         if confidence_score >= 100:
# #             print("\n✅ LLM indicates sufficient confidence.")
# #             break

# #     # ---------------- Summary ----------------
# #     specialties = kg.get_specialty_for_symptoms(entities["symptoms"])
# #     if not specialties:
# #         specialties = ["General Practitioner"]

# #     summary_prompt = f"""
# # You are an empathetic AI medical triage assistant.

# # Conversation:
# # {conversation_history}

# # Final extracted medical entities:
# # {json.dumps(entities, indent=2)}

# # Recommended medical specialties:
# # {specialties}

# # Write a concise, non-diagnostic summary including:
# # - Empathetic overview
# # - Possible causes (not diagnosis)
# # - Explicitly list recommended specialties
# # - Gentle disclaimer to consult a doctor
# # """

# #     summary = llm.invoke(summary_prompt).content

# #     print("\n🤖 MediCare AI Summary (Knowledge Graph Based):\n")
# #     print(summary)

# #     print(f"\n🎯 Final Confidence Score: {confidence_score}%")

# #     # ---------------- Doctor Finder ----------------
# #     location = input("\n📍 Enter your city/locality to find nearby specialists:\n> ")

# #     print(f"\n🧠 Suggested Specialist: {specialties[0]}")
# #     try:
# #         nearby = doctor_finder.find_doctors(specialties[0], location)
# #         if nearby:
# #             print("\n🏥 Nearby facilities:\n")
# #             for i, doc in enumerate(nearby, start=1):
# #                 print(f"{i}. {doc}")
# #         else:
# #             print("⚠️ No nearby doctors found at the moment.")
# #     except Exception as e:
# #         print(f"⚠️ Error fetching nearby doctors: {e}")

# #     print("\n🙏 Take care! This is not a medical diagnosis — please consult a healthcare professional.")


# # # -------------------------------
# # # STEP 4: Run the Chatbot
# # # -------------------------------
# # if __name__ == "__main__":
# #     run_medical_chatbot()
# #     kg.close()

# def run_medical_chatbot():
#     print("🩺 Welcome to MediCare AI — your virtual health assistant.")
#     print("Let's start your triage process.\n")

#     conversation_history = ""

#     # Persistent entities across the session
#     entities = {
#         "symptoms": [],
#         "diseases": [],
#         "medication": []
#     }

#     MAX_QUESTIONS = 5
#     questions_asked = 0

#     # ---------------- Initial Input ----------------
#     patient_input = input("🤒 Please describe your symptoms:\n> ").strip()
#     if not patient_input:
#         print("⚠️ No input provided.")
#         return

#     conversation_history += f"Patient: {patient_input}\n"

#     # Initial entity extraction
#     new_entities = extract_medical_entities(patient_input)
#     entities = merge_entities(entities, new_entities)

#     print("\n📊 Extracted Entities:")
#     print(json.dumps(entities, indent=2))

#     if not entities["symptoms"]:
#         print("\n⚠️ No clear symptoms detected. Please try again.")
#         return

#     # ---------------- Follow-up Loop ----------------
#     while questions_asked < MAX_QUESTIONS:
#         symptoms = entities["symptoms"]
#         possible_specialties = kg.get_specialty_for_symptoms(symptoms)

#         followup_prompt = f"""
# You are a medical triage assistant.

# Conversation so far:
# {conversation_history}

# Extracted entities:
# {json.dumps(entities, indent=2)}

# Possible specialties:
# {possible_specialties}

# Ask ONE short, relevant follow-up question to clarify the case.
# If no more clarification is needed, reply exactly with "DONE".
# """

#         next_q = llm.invoke(followup_prompt).content.strip()

#         if next_q.upper() == "DONE":
#             print("\n✅ No more clarification needed.")
#             break

#         questions_asked += 1
#         print(f"\n🩻 ({questions_asked}/{MAX_QUESTIONS}) {next_q}")

#         user_ans = input("> ").strip()
#         if not user_ans:
#             print("⚠️ Empty response detected. Skipping this turn.")
#             continue

#         conversation_history += f"Q: {next_q}\nA: {user_ans}\n"

#         # Update entities (merge, don’t overwrite)
#         new_entities = extract_medical_entities(user_ans)
#         entities = merge_entities(entities, new_entities)

#         print("\n📊 Updated Entities:")
#         print(json.dumps(entities, indent=2))

#     # ---------------- Summary ----------------
#     specialties = kg.get_specialty_for_symptoms(entities["symptoms"])
#     if not specialties:
#         specialties = ["General Practitioner"]

#     summary_prompt = f"""
# You are an empathetic medical triage assistant.

# Conversation:
# {conversation_history}

# Final extracted entities:
# {json.dumps(entities, indent=2)}

# Recommended specialties:
# {specialties}

# Write a concise, non-diagnostic summary including:
# - Empathetic overview
# - Possible causes (not diagnosis)
# - Explicitly list recommended specialties
# - Gentle disclaimer to consult a doctor
# """

#     summary = llm.invoke(summary_prompt).content

#     print("\n🤖 MediCare AI Summary:\n")
#     print(summary)

#     # ---------------- Doctor Finder ----------------
#     location = input("\n📍 Enter your city/locality:\n> ").strip()
#     if not location:
#         return

#     print(f"\n🧠 Suggested Specialist: {specialties[0]}")

#     try:
#         nearby = doctor_finder.find_doctors(specialties[0], location)
#         if nearby:
#             print("\n🏥 Nearby facilities:\n")
#             for i, doc in enumerate(nearby, start=1):
#                 print(f"{i}. {doc}")
#         else:
#             print("⚠️ No nearby doctors found.")
#     except Exception as e:
#         print(f"⚠️ Error fetching doctors: {e}")

#     print("\n🙏 This is not a medical diagnosis. Please consult a healthcare professional.")

import json
from langchain_community.chat_models import ChatOllama
from ner_module import extract_medical_entities
from knowledge_graph import MedicalKnowledgeGraph
from local import StandaloneDoctorFinder


# -------------------------------
# STEP 1: Setup
# -------------------------------
llm = ChatOllama(
    model="llama3",
    temperature=0.7
)

kg = MedicalKnowledgeGraph()
doctor_finder = StandaloneDoctorFinder()


# -------------------------------
# Helper: Merge entities
# -------------------------------
def merge_entities(old_entities, new_entities):
    merged = {}
    for key in ["symptoms", "diseases", "medication"]:
        merged[key] = list(
            set(old_entities.get(key, [])) |
            set(new_entities.get(key, []))
        )
    return merged


# -------------------------------
# STEP 2: Chat Logic (5 questions max)
# -------------------------------
def run_medical_chatbot():
    print("🩺 Welcome to MediCare AI — your virtual health assistant.")
    print("Let's start your triage process.\n")

    conversation_history = ""

    entities = {
        "symptoms": [],
        "diseases": [],
        "medication": []
    }

    MAX_QUESTIONS = 5
    questions_asked = 0

    # -------- Initial Input --------
    patient_input = input("🤒 Please describe your symptoms:\n> ").strip()
    if not patient_input:
        print("⚠️ No input provided.")
        return

    conversation_history += f"Patient: {patient_input}\n"

    new_entities = extract_medical_entities(patient_input)
    entities = merge_entities(entities, new_entities)

    print("\n📊 Extracted Entities:")
    print(json.dumps(entities, indent=2))

    if not entities["symptoms"]:
        print("\n⚠️ No clear symptoms detected. Please try again.")
        return

    # -------- Follow-up Loop (MAX 5) --------
    while questions_asked < MAX_QUESTIONS:
        symptoms = entities["symptoms"]
        possible_specialties = kg.get_specialty_for_symptoms(symptoms)

        followup_prompt = f"""
You are a medical triage assistant.

Conversation so far:
{conversation_history}

Extracted entities:
{json.dumps(entities, indent=2)}

Possible specialties:
{possible_specialties}

Ask ONE short, relevant follow-up question.
If no more clarification is needed, reply exactly with "DONE".
"""

        next_q = llm.invoke(followup_prompt).content.strip()

        if next_q.upper() == "DONE":
            print("\n✅ No more clarification needed.")
            break

        questions_asked += 1
        print(f"\n🩻 ({questions_asked}/{MAX_QUESTIONS}) {next_q}")

        user_ans = input("> ").strip()
        if not user_ans:
            print("⚠️ Empty response detected. Skipping.")
            continue

        conversation_history += f"Q: {next_q}\nA: {user_ans}\n"

        new_entities = extract_medical_entities(user_ans)
        entities = merge_entities(entities, new_entities)

        print("\n📊 Updated Entities:")
        print(json.dumps(entities, indent=2))

    # -------- Summary --------
    specialties = kg.get_specialty_for_symptoms(entities["symptoms"])
    if not specialties:
        specialties = ["General Practitioner"]

    summary_prompt = f"""
You are an empathetic medical triage assistant.

Conversation:
{conversation_history}

Final extracted entities:
{json.dumps(entities, indent=2)}

Recommended specialties:
{specialties}

Write a concise, non-diagnostic summary including:
- Empathetic overview
- Possible causes (not diagnosis)
- Explicitly list recommended specialties
- Gentle disclaimer to consult a doctor
"""

    summary = llm.invoke(summary_prompt).content

    print("\n🤖 MediCare AI Summary:\n")
    print(summary)

    # -------- Doctor Finder --------
    location = input("\n📍 Enter your city/locality:\n> ").strip()
    if not location:
        return

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
        print(f"⚠️ Error fetching doctors: {e}")

    print("\n🙏 This is not a medical diagnosis. Please consult a healthcare professional.")


# -------------------------------
# STEP 3: Run
# -------------------------------
if __name__ == "__main__":
    run_medical_chatbot()
    kg.close()
