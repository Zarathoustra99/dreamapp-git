from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import jinja2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conditional import for SendGrid
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not available")

load_dotenv()

# Determine which email provider to use
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "none")  # Options: 'fastapi_mail', 'sendgrid', 'none'

# Configuration for FastMail - only if it's configured
try:
    if EMAIL_PROVIDER == "fastapi_mail":
        fastapi_mail_conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME", "no-reply@example.com"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "placeholder"),
            MAIL_FROM=os.getenv("MAIL_FROM", "no-reply@example.com"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost"),
            MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "DreamApp"),
            MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "True").lower() == "true",
            MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER="./app/email_templates"
        )
    else:
        fastapi_mail_conf = None
except Exception as e:
    logger.error(f"Error configuring email: {str(e)}")
    fastapi_mail_conf = None

# SendGrid configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# Setup Jinja2 for email templates
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("./app/email_templates")
)

# Create the email templates directory if it doesn't exist
os.makedirs("./app/email_templates", exist_ok=True)


async def send_email(
    recipients: List[EmailStr],
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> None:
    """Send an email using a template."""
    try:
        # Render the template with the provided data
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**template_data)

        if EMAIL_PROVIDER == "sendgrid" and SENDGRID_AVAILABLE:
            # Use SendGrid
            if not SENDGRID_API_KEY:
                logger.warning("SendGrid API key not configured, skipping email send")
                return
                
            try:
                sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
                from_email = Email(os.getenv("MAIL_FROM", "no-reply@example.com"))
                to_emails = [To(recipient) for recipient in recipients]
                content = HtmlContent(html_content)
                
                for to_email in to_emails:
                    message = Mail(from_email=from_email, to_emails=to_email, subject=subject, html_content=content)
                    response = sg.send(message)
                    logger.info(f"Email sent via SendGrid. Status: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid: {str(e)}")
                # Don't raise the exception - just log it
                
        elif EMAIL_PROVIDER == "fastapi_mail" and fastapi_mail_conf:
            # Use FastAPI Mail
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype="html"
            )

            try:
                fm = FastMail(fastapi_mail_conf)
                await fm.send_message(message)
                logger.info(f"Email sent via FastAPI Mail to {recipients}")
            except Exception as e:
                logger.error(f"Failed to send email via FastAPI Mail: {str(e)}")
                # Don't raise the exception - just log it
        else:
            logger.warning(f"Email not sent - provider {EMAIL_PROVIDER} not configured properly")
            
    except Exception as e:
        logger.error(f"Error in send_email: {str(e)}")
        # Don't raise the exception, as we don't want email errors to break the app


async def send_verification_email(email: EmailStr, token: str) -> None:
    """Send a verification email to the user."""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    verification_url = f"{frontend_url}/verify-email?token={token}"
    
    await send_email(
        recipients=[email],
        subject="Verify Your Email Address",
        template_name="email_verification",
        template_data={
            "verification_url": verification_url,
            "username": email.split('@')[0],  # Use part before @ as username
            "app_name": os.getenv("MAIL_FROM_NAME", "DreamApp")
        }
    )


async def send_password_reset_email(email: EmailStr, token: str) -> None:
    """Send a password reset email to the user."""
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{frontend_url}/reset-password?token={token}"
    
    await send_email(
        recipients=[email],
        subject="Reset Your Password",
        template_name="password_reset",
        template_data={
            "reset_url": reset_url,
            "username": email.split('@')[0],  # Use part before @ as username
            "app_name": os.getenv("MAIL_FROM_NAME", "DreamApp")
        }
    )