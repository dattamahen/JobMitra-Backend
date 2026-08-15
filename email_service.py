"""
Email service for sending emails via SMTP.
All user-facing copy is sourced from email_constants.py.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings
from email_constants import (
    WelcomeEmail,
    PasswordResetEmail,
    VerificationEmail,
    AuthFailureEmail,
    NewUserAdminEmail,
    CvDownloadAdminEmail,
    CvDownloadUserNudgeEmail,
)

logger = logging.getLogger(__name__)


class EmailService:
    ADMIN_EMAIL = "renukadevi@jobmouka.com"
    WELCOME_FROM = "careers@jobmouka.com"
    NOREPLY_FROM = "no-reply@jobmouka.com"
    _FALLBACK_FROM = "renukadevi@jobmouka.com"  # until aliases are verified

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.app_name = settings.APP_NAME_EMAIL
        self.frontend_url = settings.FRONTEND_URL
        self.email_enabled = settings.EMAIL_ENABLED

    # ------------------------------------------------------------------ #
    #  Shared HTML shell                                                   #
    # ------------------------------------------------------------------ #

    def _build_email(self, headline: str, body_html: str) -> str:
        """Single shared template — headline and body_html are context-specific."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.6}}
  .wrap{{max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(72,49,175,.12)}}
  .header{{background:linear-gradient(135deg,#4831af 0%,#3a2590 100%);padding:36px 40px;text-align:center}}
  .logo-mark{{display:inline-block;width:48px;height:48px;background:rgba(255,255,255,.15);border-radius:12px;font-size:20px;font-weight:800;color:#fff;line-height:48px;margin-bottom:12px}}
  .logo-name{{font-size:22px;font-weight:700;color:#fff;letter-spacing:.5px}}
  .logo-name span{{color:#a78bfa}}
  .headline{{font-size:15px;color:rgba(255,255,255,.8);margin-top:6px}}
  .body{{padding:36px 40px}}
  .body p{{margin-bottom:14px;font-size:15px;color:#374151}}
  .btn{{display:inline-block;padding:13px 32px;background:linear-gradient(135deg,#4831af,#3a2590);color:#fff!important;text-decoration:none;border-radius:8px;font-weight:600;font-size:15px;margin:8px 0}}
  .btn-wrap{{text-align:center;margin:24px 0}}
  .divider{{border:none;border-top:1px solid #e5e7eb;margin:24px 0}}
  .code-box{{text-align:center;margin:20px 0}}
  .code{{display:inline-block;font-size:34px;font-weight:800;letter-spacing:8px;color:#4831af;background:#f0eef5;padding:14px 32px;border-radius:10px}}
  .link-box{{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px 16px;word-break:break-all;font-size:13px;color:#4831af;margin:12px 0}}
  .feature-list{{list-style:none;margin:12px 0 20px}}
  .feature-list li{{padding:7px 0;font-size:14px;color:#4b5563;border-bottom:1px solid #f3f4f6}}
  .feature-list li:last-child{{border-bottom:none}}
  .feature-list li::before{{content:"✓";color:#4831af;font-weight:700;margin-right:10px}}
  .note{{font-size:13px;color:#6b7280;margin-top:4px}}
  .footer{{background:#f9fafb;border-top:1px solid #e5e7eb;padding:20px 40px;text-align:center}}
  .footer p{{font-size:12px;color:#9ca3af;margin-bottom:4px}}
  .footer a{{color:#4831af;text-decoration:none}}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="logo-mark">JM</div><br/>
    <span class="logo-name">Job<span>Mouka</span></span>
    <p class="headline">{headline}</p>
  </div>
  <div class="body">
    {body_html}
  </div>
  <div class="footer">
    <p>&copy; 2026 {self.app_name}. All rights reserved.</p>
    <p><a href="https://www.jobmouka.com">www.jobmouka.com</a></p>
  </div>
</div>
</body>
</html>"""

    # ------------------------------------------------------------------ #
    #  Core send                                                           #
    # ------------------------------------------------------------------ #

    def send_email(self, to_email: str, subject: str, html_content: str,
                   from_email: str = None, reply_to: str = None) -> bool:
        """Send email via SMTP."""
        if not self.email_enabled:
            logger.debug("Email disabled. Would send to %s | Subject: %s", to_email, subject)
            return True

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        sender = from_email or self.smtp_user

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.app_name} <{sender}>"
            msg['To'] = to_email
            if reply_to:
                msg['Reply-To'] = reply_to
            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("Email sent to %s from %s", to_email, sender)
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed for user: %s", self.smtp_user)
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error("Recipient refused: %s", to_email)
            return False
        except smtplib.SMTPException as e:
            logger.error("SMTP error sending to %s: %s", to_email, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending email to %s: %s", to_email, e)
            return False

    # ------------------------------------------------------------------ #
    #  Transactional emails                                                #
    # ------------------------------------------------------------------ #

    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Welcome email for newly registered candidates."""
        ctx = dict(user_name=user_name, app_name=self.app_name, frontend_url=self.frontend_url)
        html = self._build_email(
            WelcomeEmail.HEADLINE,
            WelcomeEmail.BODY.format(**ctx),
        )
        return self.send_email(
            to_email,
            WelcomeEmail.SUBJECT.format(**ctx),
            html,
            from_email=self.WELCOME_FROM,
            reply_to=self.smtp_user,
        )

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """Password reset email."""
        reset_link = f"{self.frontend_url}/login?token={reset_token}"
        ctx = dict(user_name=user_name, app_name=self.app_name,
                   frontend_url=self.frontend_url, reset_link=reset_link)
        html = self._build_email(
            PasswordResetEmail.HEADLINE,
            PasswordResetEmail.BODY.format(**ctx),
        )
        return self.send_email(
            to_email,
            PasswordResetEmail.SUBJECT.format(**ctx),
            html,
            from_email=self.NOREPLY_FROM,
        )

    def send_verification_email(self, to_email: str, verification_token: str, user_name: str) -> bool:
        """Email verification for HR / Recruiter accounts."""
        verify_link = f"{self.frontend_url}/login?verify={verification_token}"
        code = verification_token[:6].upper()
        ctx = dict(user_name=user_name, app_name=self.app_name,
                   frontend_url=self.frontend_url, verify_link=verify_link, code=code)
        html = self._build_email(
            VerificationEmail.HEADLINE,
            VerificationEmail.BODY.format(**ctx),
        )
        return self.send_email(
            to_email,
            VerificationEmail.SUBJECT.format(**ctx),
            html,
            from_email=self.NOREPLY_FROM,
        )

    def send_auth_failure_email(self, user_email: str, user_name: str,
                                failure_type: str, reason: str) -> None:
        """Send failure notification to user and admin. Fire-and-forget."""
        type_label = "Google Sign-In" if failure_type == "google" else "Registration"
        name_part = f" <strong>{user_name}</strong>" if user_name else ""

        ctx = dict(
            app_name=self.app_name,
            frontend_url=self.frontend_url,
            type_label=type_label,
            name_part=name_part,
            user_email=user_email,
            user_name=user_name or "Unknown",
            reason=reason,
        )

        user_html = self._build_email(
            AuthFailureEmail.USER_HEADLINE.format(**ctx),
            AuthFailureEmail.USER_BODY.format(**ctx),
        )
        self.send_email(
            user_email,
            AuthFailureEmail.USER_SUBJECT.format(**ctx),
            user_html,
            from_email=self.NOREPLY_FROM,
        )

        admin_html = self._build_email(
            AuthFailureEmail.ADMIN_HEADLINE,
            AuthFailureEmail.ADMIN_BODY.format(**ctx),
        )
        self.send_email(
            self.ADMIN_EMAIL,
            AuthFailureEmail.ADMIN_SUBJECT.format(**ctx),
            admin_html,
            from_email=self.NOREPLY_FROM,
        )

    # ------------------------------------------------------------------ #
    #  New user notifications                                              #
    # ------------------------------------------------------------------ #

    def send_new_user_admin_notification(
        self, first_name: str, last_name: str, user_email: str,
        signup_method: str = "Email", user_type: str = "Candidate"
    ) -> bool:
        """Notify admin whenever a new user profile is created."""
        ctx = dict(
            app_name=self.app_name,
            first_name=first_name,
            last_name=last_name,
            user_email=user_email,
            signup_method=signup_method,
            user_type=user_type.capitalize(),
        )
        html = self._build_email(
            NewUserAdminEmail.HEADLINE,
            NewUserAdminEmail.BODY.format(**ctx),
        )
        return self.send_email(
            self.ADMIN_EMAIL,
            NewUserAdminEmail.SUBJECT.format(**ctx),
            html,
            from_email=self.NOREPLY_FROM,
        )

    # ------------------------------------------------------------------ #
    #  CV download notifications                                           #
    # ------------------------------------------------------------------ #

    def send_cv_download_admin_notification(
        self, first_name: str, last_name: str, user_email: str
    ) -> bool:
        """Notify admin when a user downloads their CV."""
        ctx = dict(app_name=self.app_name, first_name=first_name,
                   last_name=last_name, user_email=user_email)
        html = self._build_email(
            CvDownloadAdminEmail.HEADLINE,
            CvDownloadAdminEmail.BODY.format(**ctx),
        )
        return self.send_email(
            self.ADMIN_EMAIL,
            CvDownloadAdminEmail.SUBJECT.format(**ctx),
            html,
            from_email=self.NOREPLY_FROM,
        )

    def send_cv_download_user_nudge(self, to_email: str, first_name: str) -> bool:
        """Encourage user to leverage JD tailoring and mock interviews after CV download."""
        ctx = dict(app_name=self.app_name, frontend_url=self.frontend_url, first_name=first_name)
        html = self._build_email(
            CvDownloadUserNudgeEmail.HEADLINE,
            CvDownloadUserNudgeEmail.BODY.format(**ctx),
        )
        return self.send_email(
            to_email,
            CvDownloadUserNudgeEmail.SUBJECT.format(**ctx),
            html,
            from_email=self.NOREPLY_FROM,
        )


email_service = EmailService()
