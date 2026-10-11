
from unittest.mock import MagicMock, patch
import socket

from src.reporting.email_sender import send_report_email


@patch("src.reporting.email_sender.time.sleep")
@patch("src.reporting.email_sender.smtplib.SMTP")
@patch("src.reporting.email_sender.generate_report")
@patch("src.reporting.email_sender.load_dotenv")
@patch("src.reporting.email_sender.os.getenv")
def test_email_sender_retries_after_dns_failure(
    mock_getenv,
    mock_load_dotenv,
    mock_generate_report,
    mock_smtp,
    mock_sleep,
):
    # Provide fake configuration so the real .env is not needed.
    mock_getenv.side_effect = {
        "NETSENTINEL_SMTP_HOST": "smtp.example.test",
        "NETSENTINEL_SMTP_PORT": "587",
        "NETSENTINEL_EMAIL": "sender@example.test",
        "NETSENTINEL_REPORT_TO": "receiver@example.test",
        "NETSENTINEL_EMAIL_PASSWORD": "fake-password",
    }.get

    mock_generate_report.return_value = "Test report"

    # Simulate a DNS failure on attempt 1.
    # The second SMTP connection succeeds.
    mock_server = MagicMock()
    mock_server.__enter__.return_value = mock_server

    mock_smtp.side_effect = [
        socket.gaierror(-3, "Temporary DNS failure"),
        mock_server,
    ]

    # Run the email sender using mocked SMTP.
    send_report_email()

    # Verify that the sender attempted to connect twice.
    assert mock_smtp.call_count == 2

    # Verify that it waited 10 seconds before retrying.
    mock_sleep.assert_called_once_with(10)

    # Verify that the email was submitted once to the mock server.
    mock_server.send_message.assert_called_once()

    # Verify that the connection context was closed.
    mock_server.__exit__.assert_called_once()
