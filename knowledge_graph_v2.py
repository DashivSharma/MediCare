from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

class MedicalKnowledgeGraph:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")

        self.driver = GraphDatabase.driver(
            self.uri, auth=(self.user, self.password)
        )

    def close(self):
        self.driver.close()

    def populate_graph(self):
        with self.driver.session() as session:
            # ⚠️ DEV ONLY — clears DB
            session.run("MATCH (n) DETACH DELETE n")

            # Create nodes
            session.run("""
                UNWIND [
                  'fever','runny nose','cough','sore throat','body aches',
                  'chest pain','shortness of breath','headache'
                ] AS symptom
                MERGE (:Symptom {name: symptom})
            """)

            session.run("""
                UNWIND [
                  'common cold','influenza','respiratory infection','cardiac arrest'
                ] AS disease
                MERGE (:Disease {name: disease})
            """)

            session.run("""
                UNWIND [
                  'General Practitioner','Pulmonologist','Cardiologist'
                ] AS sp
                MERGE (:Specialty {name: sp})
            """)

            # Symptom → Disease with importance
            session.run("""
                MATCH (cold:Disease {name:'common cold'})
                MERGE (:Symptom {name:'runny nose'})
                    -[:HAS_SYMPTOM {importance:'REQUIRED'}]->(cold)
                MERGE (:Symptom {name:'cough'})
                    -[:HAS_SYMPTOM {importance:'OPTIONAL'}]->(cold)
                MERGE (:Symptom {name:'sore throat'})
                    -[:HAS_SYMPTOM {importance:'OPTIONAL'}]->(cold)
            """)

            session.run("""
                MATCH (flu:Disease {name:'influenza'})
                MERGE (:Symptom {name:'fever'})
                    -[:HAS_SYMPTOM {importance:'REQUIRED'}]->(flu)
                MERGE (:Symptom {name:'body aches'})
                    -[:HAS_SYMPTOM {importance:'REQUIRED'}]->(flu)
                MERGE (:Symptom {name:'cough'})
                    -[:HAS_SYMPTOM {importance:'OPTIONAL'}]->(flu)
            """)

            session.run("""
                MATCH (resp:Disease {name:'respiratory infection'})
                MERGE (:Symptom {name:'cough'})
                    -[:HAS_SYMPTOM {importance:'REQUIRED'}]->(resp)
                MERGE (:Symptom {name:'shortness of breath'})
                    -[:HAS_SYMPTOM {importance:'OPTIONAL'}]->(resp)
            """)

            session.run("""
                MATCH (cardiac:Disease {name:'cardiac arrest'})
                MERGE (:Symptom {name:'chest pain'})
                    -[:HAS_SYMPTOM {importance:'REQUIRED'}]->(cardiac)
                MERGE (:Symptom {name:'shortness of breath'})
                    -[:HAS_SYMPTOM {importance:'REQUIRED'}]->(cardiac)
            """)

            # Disease → Specialty
            session.run("""
                MATCH (cold:Disease {name:'common cold'}),
                      (flu:Disease {name:'influenza'}),
                      (gp:Specialty {name:'General Practitioner'})
                MERGE (cold)-[:REQUIRES]->(gp)
                MERGE (flu)-[:REQUIRES]->(gp)
            """)

            session.run("""
                MATCH (resp:Disease {name:'respiratory infection'}),
                      (pulmo:Specialty {name:'Pulmonologist'})
                MERGE (resp)-[:REQUIRES]->(pulmo)
            """)

            session.run("""
                MATCH (cardiac:Disease {name:'cardiac arrest'}),
                      (cardio:Specialty {name:'Cardiologist'})
                MERGE (cardiac)-[:REQUIRES]->(cardio)
            """)

            print("✅ Graph populated with symptom importance")

    # 🔍 NEW: find missing REQUIRED symptoms
    def get_missing_required_symptoms(self, disease_name, current_symptoms):
        query = """
            MATCH (s:Symptom)-[r:HAS_SYMPTOM {importance:'REQUIRED'}]->(d:Disease {name:$disease})
            WHERE NOT s.name IN $symptoms
            RETURN s.name AS missing
        """
        with self.driver.session() as session:
            result = session.run(
                query,
                disease=disease_name,
                symptoms=current_symptoms
            )
            return [r["missing"] for r in result]
    
    def get_diseases_for_symptoms(self, symptoms):
        query = """
            UNWIND $symptoms AS input
            MATCH (s:Symptom)-[:HAS_SYMPTOM]->(d:Disease)
            WHERE toLower(s.name) CONTAINS toLower(input)
            OR toLower(input) CONTAINS toLower(s.name)
            RETURN DISTINCT d.name AS disease
        """
        with self.driver.session() as session:
            result = session.run(query, symptoms=symptoms)
            return [r["disease"] for r in result]



if __name__ == "__main__":
    kg = MedicalKnowledgeGraph()
    kg.populate_graph()

    test_cases = [
        {
            "disease": "influenza",
            "symptoms": ["fever"],
        },
        {
            "disease": "influenza",
            "symptoms": ["fever", "body aches"],
        },
        {
            "disease": "common cold",
            "symptoms": ["runny nose"],
        },
        {
            "disease": "common cold",
            "symptoms": ["runny nose", "cough"],
        },
        {
            "disease": "respiratory infection",
            "symptoms": ["cough"],
        },
        {
            "disease": "cardiac arrest",
            "symptoms": ["chest pain"],
        },
        {
            "disease": "cardiac arrest",
            "symptoms": ["chest pain", "shortness of breath"],
        },
    ]

    print("\n🧪 MULTI-CASE SYMPTOM CHECK\n")

    for case in test_cases:
        missing = kg.get_missing_required_symptoms(
            case["disease"],
            case["symptoms"]
        )

        print(f"Disease: {case['disease']}")
        print(f"Current symptoms: {case['symptoms']}")
        print(f"Missing REQUIRED symptoms: {missing}")

        if not missing:
            print("🛑 STOP → Enough information collected\n")
        else:
            print("➡️ CONTINUE → Ask about:", missing[0], "\n")

    kg.close()

