import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

SENDER_EMAIL = os.getenv("MEDICARE_EMAIL")
APP_PASSWORD = os.getenv("MEDICARE_EMAIL_PASS")

# -------------------------------
# Init LLM (same model as app)
# -------------------------------
llm = ChatOllama(
    model="llama3",
    temperature=0.3
)

# -------------------------------
# MAIN FUNCTION (LLM + SMTP)
# -------------------------------
def send_email(
    *,
    summary: str,
    doctor_email: str,
    doctor_name: str,
    patient_location: str
):
    """
    1. Uses LLM to generate appointment email
    2. Sends email to doctor via SMTP
    """

    # -------- LLM PROMPT --------
    prompt = f"""
You are a professional medical assistant.

Write a polite and concise appointment request email
based on the consultation summary below.

SUMMARY:
{summary}

RULES:
- Address the doctor as: {doctor_name}
- Mention patient location: {patient_location}
- Do NOT diagnose
- Do NOT mention AI models
- Keep it professional
- End with: "Regards, MediCare AI"
"""

    email_body = llm.invoke(prompt).content.strip()

    # -------- EMAIL OBJECT --------
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = doctor_email
    msg["Subject"] = "Appointment Request — MediCare AI"
    msg.set_content(email_body)

    # -------- SEND EMAIL --------
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
