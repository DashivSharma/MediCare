import json
from langchain_community.chat_models import ChatOllama


# Initialize once (important for performance)
llm = ChatOllama(
    model="llama3",
    temperature=0
)


def extract_medical_entities(text: str) -> dict:
    """
    Extracts medical entities from text using Llama 3 (Ollama).
    Returns a structured JSON with symptoms, diseases, and medication.
    """

    prompt = f"""
You are a medical named-entity extraction system.

Extract ONLY the following entities from the text:
- symptoms
- diseases
- medication

Rules:
- Return ONLY valid JSON
- Do NOT add explanations
- If none found, return empty lists
- Use lowercase
- No markdown

JSON format:
{{
  "symptoms": [],
  "diseases": [],
  "medication": []
}}

Text:
{text}
"""

    try:
        response = llm.invoke(prompt).content.strip()

        # --- DEBUG (optional) ---
        print("\n--- RAW LLM OUTPUT ---")
        print(response)
        print("----------------------\n")

        # Force JSON parsing
        extracted = json.loads(response)

        # Ensure keys exist
        return {
            "symptoms": extracted.get("symptoms", []),
            "diseases": extracted.get("diseases", []),
            "medication": extracted.get("medication", []),
        }

    except Exception as e:
        print(f"NER error: {e}")
        return {
            "symptoms": [],
            "diseases": [],
            "medication": [],
        }


# --- Local testing ---
if __name__ == "__main__":
    tests = [
        "I have a persistent headache and mild fever with sore throat",
        "The patient was prescribed ibuprofen for chronic back pain",
        "He suffers from diabetes and hypertension",
        "A history of cardiac arrest was noted",
        "I have a skin burn and it hurts in the sun"
    ]

    for t in tests:
        print("TEXT:", t)
        print("ENTITIES:", extract_medical_entities(t))
        print()
