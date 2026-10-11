
from email.message import EmailMessage
import smtplib
import os
import socket
import time

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

    max_attempts = 5
    retry_delays = [10, 20, 30, 40]

    for attempt in range(1, max_attempts + 1):
        try:
            # Connect with a timeout so a network problem
            # cannot leave the program waiting indefinitely.
            with smtplib.SMTP(
                smtp_host, smtp_port, timeout=15
            ) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, smtp_password)
                server.send_message(message)

            print("Mail sent successfully to", receiver_email)
            return

        except (
            socket.gaierror,
            TimeoutError,
            ConnectionError,
            smtplib.SMTPServerDisconnected,
        ) as error:
            print(
                f"Temporary email connection failure "
                f"(attempt {attempt}/{max_attempts}): {error}"
            )

            if attempt == max_attempts:
                print("Email delivery failed after all retry attempts.")
                raise

            delay = retry_delays[attempt - 1]
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)


if __name__ == "__main__":
    send_report_email()
