from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv
from src.reporting.report import generate_report



def send_report_email():
    load_dotenv()
    smtp_host = os.getenv("NETSENTINEL_SMTP_HOST")
    smtp_port = int(os.getenv("NETSENTINEL_SMTP_PORT"))

    sender_email = os.getenv("NETSENTINEL_EMAIL")
    receiver_email = os.getenv("NETSENTINEL_REPORT_TO")

    smtp_password = os.getenv("NETSENTINEL_EMAIL_PASSWORD")

    message = EmailMessage()


    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Traffic report for last 6 hrs"
    report = generate_report(6)

    message.set_content(report)

    server = smtplib.SMTP(smtp_host, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(sender_email, smtp_password)
    server.send_message(message)
    server.quit()






    print("Mail sent successfully to", receiver_email)

if __name__ == "__main__":
    send_report_email()
