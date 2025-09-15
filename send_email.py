import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from agents import function_tool

# Load .env file
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

@function_tool
def send_email(to_email: str, subject: str, body: str):
    """
    Send an email using Gmail SMTP server.

    Args:
        to_email (str): The recipient's email address
        subject (str): The subject line of the email
        body (str): The main content/message of the email

    Returns:
        str: A success message if email is sent, or an error message if sending fails

    Raises:
        ValueError: If EMAIL_USER or EMAIL_PASS environment variables are not set
    """
    from_address = EMAIL_USER
    password = EMAIL_PASS

    if not from_address or not password:
        raise ValueError("EMAIL_USER and EMAIL_PASS must be set as environment variables")

    # Create email
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_address, password)
        server.sendmail(from_address, to_email, msg.as_string())
        server.quit()
        return f"✅ Email sent to {to_email}"
    except Exception as e:
        return f"❌ Failed to send email: {e}"
