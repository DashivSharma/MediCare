from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

class MedicalKnowledgeGraph:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")

        if not self.uri:
            raise ValueError("NEO4J_URI not found in .env file.")
        if not self.password:
            raise ValueError("NEO4J_PASSWORD not found in .env file.")

        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def populate_graph(self):
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")

                session.run("""
                    WITH 
                      [
                        'headache','fever','sore throat','back pain','persistent headache',
                        'mild fever','chronic back pain','stomach ache','nausea','vomiting',
                        'chest pain','shortness of breath','fatigue','joint pain','rash','cough',
                        'memory loss','numbness in limbs','dizziness','blurred vision',
                        'itchy eyes','eye redness','ear pain','hearing loss','abdominal pain',
                        'loss of appetite','weight gain','hair loss','unexplained weight loss',
                        'lump in neck','acne','itching','stiffness','difficulty walking',
                        'seizures','vision problems','irregular heartbeat','chest tightness'
                      ] AS symptoms,
                      [
                        'influenza','common cold','diabetes','hypertension','cardiac arrest',
                        'gastritis','arthritis','allergy','low back pain','neuropathy',
                        'migraine','stroke','glaucoma','ear infection','dermatitis','cancer',
                        'epilepsy','conjunctivitis','respiratory infection','rheumatoid arthritis'
                      ] AS diseases,
                      [
                        'General Practitioner','Endocrinologist','Cardiologist',
                        'Pain Management Specialist','Internal Medicine','Gastroenterologist',
                        'Allergist','Neurologist','Orthopedic Specialist','Ophthalmologist',
                        'ENT Specialist','Dermatologist','Oncologist','Pulmonologist','Rheumatologist'
                      ] AS specialties

                    UNWIND symptoms AS symptom_name
                    MERGE (:Symptom {name: symptom_name})
                    WITH diseases, specialties
                    UNWIND diseases AS disease_name
                    MERGE (:Disease {name: disease_name})
                    WITH specialties
                    UNWIND specialties AS specialty_name
                    MERGE (:Specialty {name: specialty_name});
                """)

                # Symptom → Disease relationships
                session.run("""
                    MATCH 
                        (influenza:Disease {name:'influenza'}),
                        (common_cold:Disease {name:'common cold'}),
                        (gastritis:Disease {name:'gastritis'}),
                        (cardiac_arrest:Disease {name:'cardiac arrest'}),
                        (arthritis:Disease {name:'arthritis'}),
                        (allergy:Disease {name:'allergy'}),
                        (lbp:Disease {name:'low back pain'}),
                        (neuropathy:Disease {name:'neuropathy'}),
                        (migraine:Disease {name:'migraine'}),
                        (stroke:Disease {name:'stroke'}),
                        (glaucoma:Disease {name:'glaucoma'}),
                        (ear_infection:Disease {name:'ear infection'}),
                        (dermatitis:Disease {name:'dermatitis'}),
                        (cancer:Disease {name:'cancer'}),
                        (epilepsy:Disease {name:'epilepsy'}),
                        (conj:Disease {name:'conjunctivitis'}),
                        (resp:Disease {name:'respiratory infection'}),
                        (rheum:Disease {name:'rheumatoid arthritis'})

                    // Common infections
                    MERGE (:Symptom {name:'fever'})-[:IS_A_SYMPTOM_OF]->(influenza)
                    MERGE (:Symptom {name:'sore throat'})-[:IS_A_SYMPTOM_OF]->(common_cold)
                    MERGE (:Symptom {name:'cough'})-[:IS_A_SYMPTOM_OF]->(resp)
                    MERGE (:Symptom {name:'runny nose'})-[:IS_A_SYMPTOM_OF]->(resp)

                    // Neurological
                    MERGE (:Symptom {name:'headache'})-[:IS_A_SYMPTOM_OF]->(migraine)
                    MERGE (:Symptom {name:'persistent headache'})-[:IS_A_SYMPTOM_OF]->(migraine)
                    MERGE (:Symptom {name:'seizures'})-[:IS_A_SYMPTOM_OF]->(epilepsy)
                    MERGE (:Symptom {name:'memory loss'})-[:IS_A_SYMPTOM_OF]->(stroke)
                    MERGE (:Symptom {name:'numbness in limbs'})-[:IS_A_SYMPTOM_OF]->(neuropathy)
                    MERGE (:Symptom {name:'dizziness'})-[:IS_A_SYMPTOM_OF]->(stroke)
                    MERGE (:Symptom {name:'vision problems'})-[:IS_A_SYMPTOM_OF]->(stroke)

                    // Cardio
                    MERGE (:Symptom {name:'chest pain'})-[:IS_A_SYMPTOM_OF]->(cardiac_arrest)
                    MERGE (:Symptom {name:'shortness of breath'})-[:IS_A_SYMPTOM_OF]->(resp)
                    MERGE (:Symptom {name:'irregular heartbeat'})-[:IS_A_SYMPTOM_OF]->(hypertension)
                    MERGE (:Symptom {name:'chest tightness'})-[:IS_A_SYMPTOM_OF]->(hypertension)

                    // Eyes
                    MERGE (:Symptom {name:'blurred vision'})-[:IS_A_SYMPTOM_OF]->(glaucoma)
                    MERGE (:Symptom {name:'eye redness'})-[:IS_A_SYMPTOM_OF]->(conj)
                    MERGE (:Symptom {name:'itchy eyes'})-[:IS_A_SYMPTOM_OF]->(conj)

                    // ENT
                    MERGE (:Symptom {name:'ear pain'})-[:IS_A_SYMPTOM_OF]->(ear_infection)
                    MERGE (:Symptom {name:'hearing loss'})-[:IS_A_SYMPTOM_OF]->(ear_infection)

                    // Gastro
                    MERGE (:Symptom {name:'stomach ache'})-[:IS_A_SYMPTOM_OF]->(gastritis)
                    MERGE (:Symptom {name:'nausea'})-[:IS_A_SYMPTOM_OF]->(gastritis)
                    MERGE (:Symptom {name:'loss of appetite'})-[:IS_A_SYMPTOM_OF]->(gastritis)
                    MERGE (:Symptom {name:'abdominal pain'})-[:IS_A_SYMPTOM_OF]->(gastritis)

                    // Skin
                    MERGE (:Symptom {name:'rash'})-[:IS_A_SYMPTOM_OF]->(dermatitis)
                    MERGE (:Symptom {name:'itching'})-[:IS_A_SYMPTOM_OF]->(dermatitis)
                    MERGE (:Symptom {name:'acne'})-[:IS_A_SYMPTOM_OF]->(dermatitis)

                    // Musculoskeletal
                    MERGE (:Symptom {name:'joint pain'})-[:IS_A_SYMPTOM_OF]->(rheum)
                    MERGE (:Symptom {name:'stiffness'})-[:IS_A_SYMPTOM_OF]->(rheum)
                    MERGE (:Symptom {name:'difficulty walking'})-[:IS_A_SYMPTOM_OF]->(rheum)
                    MERGE (:Symptom {name:'chronic back pain'})-[:IS_A_SYMPTOM_OF]->(lbp)

                    // Others
                    MERGE (:Symptom {name:'weight gain'})-[:IS_A_SYMPTOM_OF]->(diabetes)
                    MERGE (:Symptom {name:'hair loss'})-[:IS_A_SYMPTOM_OF]->(diabetes)
                    MERGE (:Symptom {name:'unexplained weight loss'})-[:IS_A_SYMPTOM_OF]->(cancer)
                    MERGE (:Symptom {name:'lump in neck'})-[:IS_A_SYMPTOM_OF]->(cancer);
                """)

                # Disease → Specialty relationships
                session.run("""
                    MATCH
                        (influenza:Disease {name:'influenza'}),
                        (common_cold:Disease {name:'common cold'}),
                        (diabetes:Disease {name:'diabetes'}),
                        (hypertension:Disease {name:'hypertension'}),
                        (cardiac_arrest:Disease {name:'cardiac arrest'}),
                        (gastritis:Disease {name:'gastritis'}),
                        (arthritis:Disease {name:'arthritis'}),
                        (allergy:Disease {name:'allergy'}),
                        (lbp:Disease {name:'low back pain'}),
                        (neuropathy:Disease {name:'neuropathy'}),
                        (migraine:Disease {name:'migraine'}),
                        (stroke:Disease {name:'stroke'}),
                        (glaucoma:Disease {name:'glaucoma'}),
                        (ear_infection:Disease {name:'ear infection'}),
                        (dermatitis:Disease {name:'dermatitis'}),
                        (cancer:Disease {name:'cancer'}),
                        (epilepsy:Disease {name:'epilepsy'}),
                        (conj:Disease {name:'conjunctivitis'}),
                        (resp:Disease {name:'respiratory infection'}),
                        (rheum:Disease {name:'rheumatoid arthritis'}),
                        (gp:Specialty {name:'General Practitioner'}),
                        (endo:Specialty {name:'Endocrinologist'}),
                        (cardio:Specialty {name:'Cardiologist'}),
                        (pain:Specialty {name:'Pain Management Specialist'}),
                        (im:Specialty {name:'Internal Medicine'}),
                        (gastro:Specialty {name:'Gastroenterologist'}),
                        (allergist:Specialty {name:'Allergist'}),
                        (neuro:Specialty {name:'Neurologist'}),
                        (ortho:Specialty {name:'Orthopedic Specialist'}),
                        (ophth:Specialty {name:'Ophthalmologist'}),
                        (ent:Specialty {name:'ENT Specialist'}),
                        (derma:Specialty {name:'Dermatologist'}),
                        (onco:Specialty {name:'Oncologist'}),
                        (pulmo:Specialty {name:'Pulmonologist'}),
                        (rheuma:Specialty {name:'Rheumatologist'})

                    MERGE (influenza)-[:REQUIRES]->(gp)
                    MERGE (common_cold)-[:REQUIRES]->(gp)
                    MERGE (resp)-[:REQUIRES]->(pulmo)
                    MERGE (gastritis)-[:REQUIRES]->(gastro)
                    MERGE (arthritis)-[:REQUIRES]->(rheuma)
                    MERGE (allergy)-[:REQUIRES]->(allergist)
                    MERGE (lbp)-[:REQUIRES]->(pain)
                    MERGE (neuropathy)-[:REQUIRES]->(neuro)
                    MERGE (migraine)-[:REQUIRES]->(neuro)
                    MERGE (stroke)-[:REQUIRES]->(neuro)
                    MERGE (epilepsy)-[:REQUIRES]->(neuro)
                    MERGE (glaucoma)-[:REQUIRES]->(ophth)
                    MERGE (conj)-[:REQUIRES]->(ophth)
                    MERGE (ear_infection)-[:REQUIRES]->(ent)
                    MERGE (dermatitis)-[:REQUIRES]->(derma)
                    MERGE (cancer)-[:REQUIRES]->(onco)
                    MERGE (cardiac_arrest)-[:REQUIRES]->(cardio)
                    MERGE (hypertension)-[:REQUIRES]->(cardio)
                    MERGE (diabetes)-[:REQUIRES]->(endo);
                """)

            print("✅ Expanded graph populated successfully with 40+ specialties.")
        except Exception as e:
            print(f"❌ Error populating graph: {e}")

    def get_specialty_for_symptoms(self, symptoms: list) -> list:
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        query_string = """
            UNWIND $symptoms AS input_symptom
            MATCH (s:Symptom)-[:IS_A_SYMPTOM_OF]->(d:Disease)-[:REQUIRES]->(sp:Specialty)
            WHERE toLower(input_symptom) CONTAINS toLower(s.name)
               OR toLower(s.name) CONTAINS toLower(input_symptom)
            RETURN DISTINCT sp.name AS specialty
        """
        try:
            with self.driver.session() as session:
                result = session.run(query_string, symptoms=symptoms)
                return [record["specialty"] for record in result]
        except Exception as e:
            print(f"Error while querying graph: {e}")
            return []


if __name__ == '__main__':
    kg = MedicalKnowledgeGraph()
    kg.populate_graph()

    print("\n=== 🩺 TESTING MEDICAL SPECIALTY RECOMMENDATIONS ===\n")

    test_cases = [
        ["persistent headache", "mild fever", "sore throat"],
        ["runny nose", "mild fever", "cough"],
        ["chest pain", "shortness of breath"],
        ["irregular heartbeat", "fatigue", "chest tightness"],
        ["seizures", "memory loss", "numbness in limbs"],
        ["dizziness", "headache", "vision problems"],
        ["chronic back pain"],
        ["joint pain", "stiffness", "difficulty walking"],
        ["blurred vision", "eye redness", "itchy eyes"],
        ["ear pain", "sore throat", "hearing loss"],
        ["abdominal pain", "nausea", "loss of appetite"],
        ["weight gain", "fatigue", "hair loss"],
        ["unexplained weight loss", "persistent fatigue", "lump in neck"],
        ["rashes", "itching", "acne"],
        ["dizziness", "blurry vision", "nausea"],
        ["random pain", "strange sensation"],
    ]

    for symptoms in test_cases:
        specialties = kg.get_specialty_for_symptoms(symptoms)
        print(f"Symptoms: {symptoms}\n→ Recommended Specialties: {specialties}\n")

    kg.close()
