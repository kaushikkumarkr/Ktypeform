
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.enabled = bool(settings.SMTP_HOST)
    
    def send_submission_email(self, to_email: str, pdf_url: str, form_title: str):
        """
        Sends an email with the PDF link.
        If SMTP is not configured, mocks the email by logging it.
        """
        subject = f"Your Form Submission: {form_title}"
        body = f"""
        <h1>Submission Received</h1>
        <p>Thank you for submitting <b>{form_title}</b>.</p>
        <p>You can download your PDF copy here:</p>
        <p><a href="{pdf_url}">Download PDF</a></p>
        <br>
        <p>Regards,<br>Smart Form Automation</p>
        """

        if not self.enabled:
            logger.info("------------------------------------------------")
            logger.info(f"[MOCK EMAIL] To: {to_email}")
            logger.info(f"[MOCK EMAIL] Subject: {subject}")
            logger.info(f"[MOCK EMAIL] Body: {body}")
            logger.info("------------------------------------------------")
            return

        try:
            msg = MIMEMultipart()
            msg["From"] = settings.EMAILS_FROM_EMAIL
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
            
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")

email_service = EmailService()
