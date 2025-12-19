# from knowledge_graph_v2 import MedicalKnowledgeGraph
# from langchain_community.llms import Ollama

# # ----------------- INIT KG -----------------
# kg = MedicalKnowledgeGraph()

# # ----------------- INIT LLM -----------------
# llm = Ollama(model="llama3")

# # ----------------- HELPERS -----------------
# def merge_entities(old, new):
#     for key in old:
#         old[key] = list(set(old[key]) | set(new.get(key, [])))
#     return old


# # def extract_medical_entities(text):
# #     """
# #     Simple, reliable keyword-based symptom extractor.
# #     """
# #     KNOWN_SYMPTOMS = [
# #         "fever", "runny nose", "cough", "sore throat",
# #         "body aches", "chest pain", "shortness of breath",
# #         "headache", "nausea", "vomiting", "dizziness"
# #     ]

# #     text = text.lower()
# #     found = []

# #     for symptom in KNOWN_SYMPTOMS:
# #         if symptom in text:
# #             found.append(symptom)

# #     return {
# #         "symptoms": found,
# #         "diseases": [],
# #         "medication": []
# #     }
# def extract_medical_entities(text, llm):
#     """
#     Uses LLM to extract and normalize symptoms into
#     canonical medical terms understood by the KG.
#     """

#     prompt = f"""
# You are a medical text normalizer.

# From the text below, extract ONLY symptoms
# and normalize them to simple medical terms
# (e.g., "pain in the back of my throat" → "sore throat").

# Rules:
# - Return ONLY a JSON object
# - Use lowercase
# - Use common symptom names
# - If no symptoms found, return an empty list

# Text:
# \"\"\"{text}\"\"\"

# Format:
# {{
#   "symptoms": ["symptom1", "symptom2"]
# }}
# """

#     response = llm.invoke(prompt)

#     try:
#         data = json.loads(response)
#         return {
#             "symptoms": data.get("symptoms", []),
#             "diseases": [],
#             "medication": []
#         }
#     except Exception:
#         # Safe fallback
#         return {
#             "symptoms": [],
#             "diseases": [],
#             "medication": []
#         }


# def get_next_missing_symptom(symptoms):
#     """
#     Uses Knowledge Graph to determine:
#     - what disease is likely
#     - what REQUIRED symptom is missing
#     - whether to STOP
#     """
#     candidate_diseases = kg.get_diseases_for_symptoms(symptoms)

#     for disease in candidate_diseases:
#         missing = kg.get_missing_required_symptoms(disease, symptoms)
#         if missing:
#             return disease, missing[0]
#         else:
#             return disease, None  # STOP condition

#     return None, None


# # ----------------- MAIN CHATBOT -----------------
# def run_medical_chatbot():
#     print("🩺 Welcome to MediCare AI — your virtual health assistant.")
#     print("Let's start your triage process.\n")

#     entities = {
#         "symptoms": [],
#         "diseases": [],
#         "medication": []
#     }

#     MAX_QUESTIONS = 5
#     questions_asked = 0
#     conversation_history = ""

#     # -------- Initial Input --------
#     patient_input = input("🤒 Please describe your symptoms:\n> ").strip()
#     if not patient_input:
#         print("⚠️ No input provided.")
#         return

#     conversation_history += f"Patient: {patient_input}\n"

#     new_entities = extract_medical_entities(patient_input,llm)
#     entities = merge_entities(entities, new_entities)

#     if not entities["symptoms"]:
#         print("⚠️ No clear symptoms detected. Please consult a doctor.")
#         return

#     print("\n📊 Extracted Symptoms:", entities["symptoms"])

#     # -------- Follow-up Loop --------
#     while questions_asked < MAX_QUESTIONS:
#         disease, missing_symptom = get_next_missing_symptom(
#             entities["symptoms"]
#         )

#         if missing_symptom is None:
#             print("\n🛑 Enough information collected.")
#             break

#         questions_asked += 1

#         # LLM ONLY for phrasing
#         prompt = f"""
# Ask a short, polite yes/no medical follow-up question
# to check whether the patient has this symptom:
# {missing_symptom}
# """
#         question = llm.invoke(prompt).strip()

#         print(f"\n🩻 ({questions_asked}/{MAX_QUESTIONS}) {question}")
#         answer = input("> ").strip()

#         conversation_history += f"Q: {question}\nA: {answer}\n"

#         new_entities = extract_medical_entities(answer,llm)
#         entities = merge_entities(entities, new_entities)

#         print("📊 Updated Symptoms:", entities["symptoms"])

#     # -------- Summary --------
#     summary_prompt = f"""
# You are an empathetic medical triage assistant.

# Conversation:
# {conversation_history}

# Symptoms identified:
# {entities["symptoms"]}

# Write a concise summary including:
# - Empathetic overview
# - Possible condition patterns (not diagnosis)
# - Recommended next step
# - Gentle disclaimer to consult a doctor
# """

#     summary = llm.invoke(summary_prompt)

#     print("\n🤖 MediCare AI Summary:\n")
#     print(summary)

#     print("\n🙏 This is not a medical diagnosis. Please consult a healthcare professional.")


# # ----------------- ENTRY POINT -----------------
# if __name__ == "__main__":
#     run_medical_chatbot()

from langchain_community.llms import Ollama
import json

# ----------------- INIT LLM -----------------
llm = Ollama(model="llama3")

# ----------------- HELPERS -----------------
def merge_entities(old, new):
    old["symptoms"] = list(set(old["symptoms"] + new.get("symptoms", [])))
    return old


def extract_medical_entities(text):
    """
    Let LLM extract symptoms freely.
    """
    prompt = f"""
You are a medical assistant.

From the text below, extract symptoms mentioned by the user.

Rules:
- Return ONLY valid JSON
- Use simple symptom names
- If none, return empty list

Text:
\"\"\"{text}\"\"\"

Format:
{{
  "symptoms": []
}}
"""
    response = llm.invoke(prompt)

    try:
        data = json.loads(response)
        return {
            "symptoms": data.get("symptoms", []),
            "diseases": [],
            "medication": []
        }
    except Exception:
        return {"symptoms": [], "diseases": [], "medication": []}


# ----------------- MAIN CHATBOT -----------------
def run_medical_chatbot():
    print("🩺 Welcome to MediCare AI — your virtual health assistant.")
    print("Let's understand your condition step by step.\n")

    entities = {
        "symptoms": [],
        "diseases": [],
        "medication": []
    }

    MAX_QUESTIONS = 6
    questions_asked = 0
    conversation_history = ""

    # -------- Initial Input --------
    user_input = input("🤒 Please describe your symptoms:\n> ").strip()
    if not user_input:
        print("⚠️ No input provided.")
        return

    conversation_history += f"Patient: {user_input}\n"

    new_entities = extract_medical_entities(user_input)
    entities = merge_entities(entities, new_entities)

    print("\n📊 Current symptoms:", entities["symptoms"])

    # -------- Follow-up Loop --------
    while questions_asked < MAX_QUESTIONS:
        followup_prompt = f"""
You are a careful medical triage assistant.

Known symptoms so far:
{entities["symptoms"]}

Conversation so far:
{conversation_history}

Ask ONE relevant follow-up question to clarify the condition.
If no more clarification is needed, reply exactly with "DONE".
"""

        next_question = llm.invoke(followup_prompt).strip()

        if next_question.upper() == "DONE":
            break

        questions_asked += 1
        print(f"\n🩻 ({questions_asked}/{MAX_QUESTIONS}) {next_question}")
        answer = input("> ").strip()

        conversation_history += f"Q: {next_question}\nA: {answer}\n"

        new_entities = extract_medical_entities(answer)
        entities = merge_entities(entities, new_entities)

        print("📊 Updated symptoms:", entities["symptoms"])

    # -------- Summary --------
    summary_prompt = f"""
You are an empathetic medical assistant.

Conversation:
{conversation_history}

Final symptoms:
{entities["symptoms"]}

Write a concise, non-diagnostic summary including:
- What the symptoms suggest
- Possible causes (not diagnosis)
- Recommended next steps
- Gentle disclaimer
"""

    summary = llm.invoke(summary_prompt)

    print("\n🤖 MediCare AI Summary:\n")
    print(summary)

    print("\n🙏 This is not a medical diagnosis. Please consult a healthcare professional.")


# ----------------- ENTRY POINT -----------------
if __name__ == "__main__":
    run_medical_chatbot()
