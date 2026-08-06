"""
Email service for sending emails via SMTP
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    WELCOME_FROM = "careers@jobmouka.com"      # requires Gmail alias verification
    NOREPLY_FROM = "no-reply@jobmouka.com"     # requires Gmail alias verification
    _FALLBACK_FROM = "renukadevi@jobmouka.com" # used until aliases are verified

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.app_name = settings.APP_NAME_EMAIL
        self.frontend_url = settings.FRONTEND_URL
        self.email_enabled = settings.EMAIL_ENABLED

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

    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Welcome email for newly registered candidates."""
        body = f"""
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>Welcome to <strong>{self.app_name}</strong> — your AI-powered career platform. We're thrilled to have you on board!</p>
        <p>Here's what you can do right now:</p>
        <ul class="feature-list">
          <li>Build an ATS-optimized resume with AI</li>
          <li>Search and apply to 10,000+ job listings</li>
          <li>Practice mock interviews with AI feedback</li>
          <li>Get match analysis for every job you apply to</li>
        </ul>
        <div class="btn-wrap">
          <a href="{self.frontend_url}/dashboard" class="btn">Go to Dashboard</a>
        </div>
        <p class="note">If you have any questions, just reply to this email — we're happy to help.</p>
        """
        html = self._build_email("Welcome aboard! 🎉", body)
        return self.send_email(to_email, f"Welcome to {self.app_name} 🎉", html,
                               from_email=self.WELCOME_FROM, reply_to=self.smtp_user)

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """Password reset email."""
        reset_link = f"{self.frontend_url}/login?token={reset_token}"
        body = f"""
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>We received a request to reset your <strong>{self.app_name}</strong> password. Click the button below to set a new one:</p>
        <div class="btn-wrap">
          <a href="{reset_link}" class="btn">Reset My Password</a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <div class="link-box">{reset_link}</div>
        <hr class="divider"/>
        <p class="note">⏱ This link expires in <strong>1 hour</strong>.</p>
        <p class="note">If you didn't request this, you can safely ignore this email — your password won't change.</p>
        """
        html = self._build_email("Password Reset Request", body)
        return self.send_email(to_email, f"Reset Your {self.app_name} Password", html, from_email=self.NOREPLY_FROM)

    def send_verification_email(self, to_email: str, verification_token: str, user_name: str) -> bool:
        """Email verification for HR / Recruiter accounts."""
        verify_link = f"{self.frontend_url}/login?verify={verification_token}"
        code = verification_token[:6].upper()
        body = f"""
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>Thank you for registering as an HR / Recruiter on <strong>{self.app_name}</strong>.</p>
        <p>To activate your account and start posting jobs, please verify your email:</p>
        <div class="btn-wrap">
          <a href="{verify_link}" class="btn">Verify My Account</a>
        </div>
        <p style="text-align:center;font-size:14px;color:#6b7280;">Or use this one-time code:</p>
        <div class="code-box"><span class="code">{code}</span></div>
        <p>Or copy and paste this link:</p>
        <div class="link-box">{verify_link}</div>
        <hr class="divider"/>
        <p class="note">⏱ This link expires in <strong>24 hours</strong>.</p>
        <p style="font-size:14px;color:#4b5563;margin-top:16px;">Once verified, you'll be able to:</p>
        <ul class="feature-list">
          <li>Post job openings</li>
          <li>View and manage applications</li>
          <li>Access candidate profiles</li>
        </ul>
        """
        html = self._build_email("Verify Your HR Account", body)
        return self.send_email(to_email, f"Verify Your {self.app_name} HR Account", html, from_email=self.NOREPLY_FROM)


    ADMIN_EMAIL = "renukadevi@jobmouka.com"

    def send_auth_failure_email(self, user_email: str, user_name: str, failure_type: str, reason: str) -> None:
        """Send failure notification to user and admin. Fire-and-forget."""
        type_label = "Google Sign-In" if failure_type == "google" else "Registration"

        # Email to user
        user_body = f"""
        <p>Hi{' <strong>' + user_name + '</strong>' if user_name else ''},</p>
        <p>We noticed a failed <strong>{type_label}</strong> attempt on your account.</p>
        <p>If this was you, please try again or contact support. If it wasn't you, your account is safe — no action is needed.</p>
        <div class="btn-wrap">
          <a href="{self.frontend_url}/login" class="btn">Go to Login</a>
        </div>
        <p class="note">If you need help, reply to this email.</p>
        """
        user_html = self._build_email(f"{type_label} Failed", user_body)
        self.send_email(user_email, f"{self.app_name} — {type_label} Failed", user_html,
                        from_email=self.NOREPLY_FROM)

        # Email to admin
        admin_body = f"""
        <p><strong>Auth Failure Alert</strong></p>
        <p><strong>Type:</strong> {type_label}</p>
        <p><strong>User Email:</strong> {user_email}</p>
        <p><strong>Name:</strong> {user_name or 'Unknown'}</p>
        <p><strong>Reason:</strong> {reason}</p>
        """
        admin_html = self._build_email("Auth Failure Alert", admin_body)
        self.send_email(self.ADMIN_EMAIL, f"[{self.app_name}] Auth Failure — {user_email}",
                        admin_html, from_email=self.NOREPLY_FROM)


email_service = EmailService()
