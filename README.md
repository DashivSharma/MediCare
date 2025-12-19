🩺 MediCare AI — Intelligent Medical Triage & Appointment Assistant

MediCare AI is an LLM-powered medical triage system that interacts with users to understand their symptoms, recommends the most appropriate medical specialist, and allows users to book an appointment by automatically sending a professional email to the selected clinic.

The system combines LLMs, a medical knowledge graph, NER, and a Streamlit UI, while enforcing hard safety stops to avoid over-questioning or diagnosis.

✨ Key Features

🤖 AI-driven medical triage

🧠 Knowledge Graph–guided specialist recommendation

🛑 Hardcoded safety stop (max follow-up questions)

💬 Conversational chat interface (Streamlit)

📍 Nearby doctor/clinic discovery

📧 LLM-generated appointment email

🔐 Secure email sending using SMTP + .env

🧱 Clean separation between agent logic and UI

🏗️ Architecture Overview
User → Streamlit UI
        ↓
agent_workflow_v3 (Medical Reasoning)
        ↓
Medical Knowledge Graph + NER
        ↓
Specialist Recommendation
        ↓
Doctor Finder
        ↓
LLM-generated Appointment Email
        ↓
SMTP (Gmail) → Clinic

📁 Project Structure
├── app.py                  # Streamlit UI
├── agent_workflow_v3.py    # Core medical triage logic (agent)
├── ner_module.py           # Symptom/entity extraction
├── knowledge_graph.py      # Symptom → specialty mapping
├── local.py                # Doctor & clinic discovery
├── email_send.py           # LLM-powered email sender (SMTP)
├── .env                    # Email credentials (ignored by git)
├── requirements.txt
└── README.md

🧠 Medical Triage Logic

Extracts symptoms using NER

Uses a Medical Knowledge Graph to map symptoms → specialties

Asks at most 2 follow-up questions (hardcoded stop)

Prevents diagnosis and overconfidence

Falls back safely to General Practitioner if needed

⚠️ This system is not a diagnostic tool and always includes medical disclaimers.

📧 Appointment Booking Flow

User completes triage

System recommends a specialist

Nearby clinics are displayed

User clicks Book Appointment

LLM generates a professional email using chat summary

Email is sent to the clinic via SMTP

User receives confirmation in the UI

🔐 Email Setup (Required)

This project uses Gmail App Passwords for secure email sending.

1️⃣ Create a Gmail account (recommended)

Example:

medicare.ai.project@gmail.com

2️⃣ Enable 2-Step Verification

Google Account → Security → 2-Step Verification

3️⃣ Generate App Password

App: Mail

Device: Other (name it MediCare AI)

Copy the 16-character password

🌱 Environment Variables (.env)

Create a .env file in the project root:

MEDICARE_EMAIL=medicare.ai.project@gmail.com
MEDICARE_EMAIL_PASS=your_16_character_app_password


⚠️ Make sure .env is added to .gitignore.

🚀 How to Run the Project
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start Ollama (LLM backend)
ollama run llama3

3️⃣ Run the Streamlit app
streamlit run app.py

🧪 Testing Tips

Use your own email as a clinic email for testing

Check Spam folder on first email

Ensure Ollama is running before starting Streamlit

🛡️ Safety & Design Decisions

❌ No medical diagnosis

❌ No unlimited questioning

✅ Hard stop on follow-up questions

✅ Explicit disclaimers

✅ Agent logic separated from UI

✅ Secrets stored securely in .env

🧩 Technologies Used

Python

Streamlit

LangChain

Ollama (LLaMA 3)

SMTP (Gmail)

dotenv

Knowledge Graph

Named Entity Recognition (NER)

📌 Future Improvements

📅 Appointment date & time selection

📩 Email confirmation to patient

📎 PDF consultation summary

🧪 Mock email mode for demos

🔐 Authentication & user profiles

⚠️ Disclaimer

MediCare AI is an educational and research project.
It does not provide medical diagnosis or treatment.
Always consult a licensed medical professional.
