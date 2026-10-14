"""
Email service for sending emails via SMTP.
All user-facing copy is sourced from email_constants.py.
"""
import logging
import os
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
    InternalJobAppliedPosterEmail,
    InternalJobAppliedCandidateEmail,
    ContestSparkConfirmedEmail,
    ContestSparkConfirmedNewUserEmail,
    ContestBlueprintOpenEmail,
    ContestBlueprintResultEmail,
    ContestProofOpenEmail,
    ContestProofResultEmail,
    ContestInterviewScheduledEmail,
    ContestInterviewCompleteEmail,
    ContestWinnerEmail,
    ContestEliminatedEmail,
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
        # Re-read at send time — Cloud Run secrets may not be available at import time
        email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        smtp_user = os.getenv("SMTP_USER", self.smtp_user)
        smtp_password = os.getenv("SMTP_PASSWORD", self.smtp_password)

        logger.info("Email send attempt: enabled=%s, user=%s, to=%s", email_enabled, smtp_user, to_email)

        if not email_enabled:
            logger.info("Email disabled (EMAIL_ENABLED=%s). Skipping send to %s", os.getenv('EMAIL_ENABLED'), to_email)
            return True

        if not smtp_user or not smtp_password:
            logger.warning("SMTP credentials not configured (SMTP_USER=%s)", bool(smtp_user))
            return False

        sender = from_email or smtp_user

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
                server.login(smtp_user, smtp_password)
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
        )

        admin_html = self._build_email(
            AuthFailureEmail.ADMIN_HEADLINE,
            AuthFailureEmail.ADMIN_BODY.format(**ctx),
        )
        self.send_email(
            self.ADMIN_EMAIL,
            AuthFailureEmail.ADMIN_SUBJECT.format(**ctx),
            admin_html,
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
        )


    def send_internal_job_applied_poster(self, poster_email: str, job: dict, applicant: dict, applied_date: str, match_percentage=None) -> bool:
        """Notify job poster with full candidate profile snapshot."""
        def _row(label, value):
            if not value:
                return ""
            return f'<tr><td style="padding:10px 14px;color:#6b7280;width:38%;border-bottom:1px solid #e5e7eb;">{label}</td><td style="padding:10px 14px;color:#111827;border-bottom:1px solid #e5e7eb;">{value}</td></tr>'

        skills = applicant.get("skills") or []
        skills_block = ""
        if skills:
            chips = "".join(f'<span style="display:inline-block;background:#ede9fe;color:#4831af;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;margin:3px;">{s}</span>' for s in skills[:12])
            skills_block = f'<p style="font-size:14px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">&#127919; Skills</p><div style="margin-bottom:8px;">{chips}</div>'
            if len(skills) > 12:
                skills_block += f'<p style="font-size:12px;color:#6b7280;">+{len(skills)-12} more skills on profile</p>'

        summary = (applicant.get("professional_summary") or "")[:300]
        summary_block = ""
        if summary:
            summary_block = f'<p style="font-size:14px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">&#128203; Professional Summary</p><p style="font-size:14px;color:#4b5563;background:#f9fafb;border-radius:8px;padding:12px 16px;">{summary}{"..." if len(applicant.get("professional_summary","")) > 300 else ""}</p>'

        links = []
        if applicant.get("linkedin_link"):
            links.append(f'<a href="{applicant["linkedin_link"]}" style="color:#4831af;margin-right:16px;">&#128279; LinkedIn</a>')
        if applicant.get("github_link"):
            links.append(f'<a href="{applicant["github_link"]}" style="color:#4831af;margin-right:16px;">&#128187; GitHub</a>')
        if applicant.get("portfolio_link"):
            links.append(f'<a href="{applicant["portfolio_link"]}" style="color:#4831af;">&#127760; Portfolio</a>')
        links_block = ""
        if links:
            links_block = f'<p style="font-size:14px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">&#128279; Links</p><p>{" ".join(links)}</p>'

        city = applicant.get("city") or ""
        state = applicant.get("state") or ""
        location = ", ".join(filter(None, [city, state]))

        exp = applicant.get("overall_experience_years")
        exp_str = f"{exp} year{'s' if exp != 1 else ''}" if exp else ""

        match_row = _row("Match Score", f"{match_percentage}%" if match_percentage else "")

        job_id = job.get("internal_job_id", "")
        wa_text = (
            f"\U0001f680 *{job.get('title', '')}* at *{job.get('company', '')}*\n"
            f"\U0001f4cb Job ID: {job_id}\n\n"
            f"Apply now on JobMouka:\n"
            f"\U0001f310 https://www.jobmouka.com\n"
            f"\U0001f4f1 Play Store: https://play.google.com/store/apps/details?id=com.jobmouka.app"
        )
        import urllib.parse
        whatsapp_share_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

        ctx = dict(
            app_name=self.app_name,
            frontend_url=self.frontend_url,
            job_title=job.get("title", ""),
            company=job.get("company", ""),
            applicant_name=f"{applicant.get('first_name','')} {applicant.get('last_name','')}".strip(),
            applicant_email=applicant.get("email", ""),
            phone_row=_row("Phone", applicant.get("phone", "")),
            experience_row=_row("Experience", exp_str),
            current_role_row=_row("Current Role", applicant.get("current_role") or applicant.get("professional_info", {}).get("current_role", "")),
            location_row=_row("Location", location),
            applied_date=applied_date,
            match_row=match_row,
            skills_block=skills_block,
            summary_block=summary_block,
            links_block=links_block,
            whatsapp_share_url=whatsapp_share_url,
        )
        html = self._build_email(InternalJobAppliedPosterEmail.HEADLINE, InternalJobAppliedPosterEmail.BODY.format(**ctx))
        return self.send_email(poster_email, InternalJobAppliedPosterEmail.SUBJECT.format(**ctx), html, reply_to=applicant.get("email"))

    def send_internal_job_applied_candidate(self, to_email: str, applicant_name: str, job: dict, applied_date: str, match_percentage=None) -> bool:
        """Confirmation email to the candidate who just applied."""
        match_row = ""
        if match_percentage:
            match_row = f'<tr><td style="padding:6px 0;color:#6b7280;">Match Score</td><td style="padding:6px 0;color:#16a34a;font-weight:700;">{match_percentage}%</td></tr>'
        ctx = dict(
            app_name=self.app_name,
            frontend_url=self.frontend_url,
            applicant_name=applicant_name,
            job_title=job.get("title", ""),
            company=job.get("company", ""),
            applied_date=applied_date,
            match_row=match_row,
        )
        html = self._build_email(InternalJobAppliedCandidateEmail.HEADLINE, InternalJobAppliedCandidateEmail.BODY.format(**ctx))
        return self.send_email(to_email, InternalJobAppliedCandidateEmail.SUBJECT.format(**ctx), html)

    # ------------------------------------------------------------------ #
    #  Project Contest emails                                              #
    # ------------------------------------------------------------------ #

    def _contest_result_blocks(self, score: int, threshold: int, advance: bool) -> tuple[str, str, str, str]:
        """Return (result_emoji, result_label, result_color, result_bg) based on outcome."""
        if advance:
            return "✅", f"Advanced to next level!", "#16a34a", "#f0fdf4"
        return "❌", f"Did not meet the threshold ({threshold}/100)", "#dc2626", "#fef2f2"

    def send_contest_spark_confirmed(self, recipients: list[dict], entry: dict) -> None:
        """Send Level 1 confirmation to all team members.
        recipients: [{ name, email, is_registered }]
        """
        category = entry.get("category", "").replace("_", " ").title()
        for r in recipients:
            cls = ContestSparkConfirmedEmail if r["is_registered"] else ContestSparkConfirmedNewUserEmail
            ctx = dict(
                app_name=self.app_name,
                frontend_url=self.frontend_url,
                recipient_name=r["name"],
                lead_name=entry["lead_name"],
                project_title=entry["refined_title"] or entry["raw_project_name"],
                entry_id=entry["entry_id"],
                category=category,
                team_size=entry["team_size"],
            )
            html = self._build_email(cls.HEADLINE, cls.BODY.format(**ctx))
            self.send_email(r["email"], cls.SUBJECT.format(**ctx), html)

    def send_contest_blueprint_open(self, recipients: list[dict], entry: dict) -> None:
        """Send Level 2 open notification to all team members."""
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        for r in recipients:
            ctx = dict(
                app_name=self.app_name,
                frontend_url=self.frontend_url,
                recipient_name=r["name"],
                project_title=project_title,
            )
            html = self._build_email(ContestBlueprintOpenEmail.HEADLINE, ContestBlueprintOpenEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestBlueprintOpenEmail.SUBJECT.format(**ctx), html)

    def send_contest_blueprint_result(self, recipients: list[dict], entry: dict,
                                      score: int, feedback: str, advance: bool) -> None:
        """Send Level 2 evaluation result to all team members."""
        from project_contest_schemas import SCORE_THRESHOLDS
        threshold = SCORE_THRESHOLDS["blueprint"]
        emoji, label, color, bg = self._contest_result_blocks(score, threshold, advance)
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        next_steps_block = (
            '<p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">&#127381; What\'s next?</p>'
            '<p style="font-size:14px;color:#4b5563;">Level 3 — <strong>Proof</strong> — will open in 30 days. '
            'Prepare your working demo video and GitHub repository.</p>'
        ) if advance else (
            '<p style="font-size:14px;color:#4b5563;">Thank you for participating. '
            'Use your Mock Interview credits to keep building your skills.</p>'
        )
        for r in recipients:
            ctx = dict(
                app_name=self.app_name, frontend_url=self.frontend_url,
                recipient_name=r["name"], project_title=project_title,
                score=score, result_emoji=emoji, result_label=label,
                result_color=color, result_bg=bg, feedback=feedback,
                next_steps_block=next_steps_block,
            )
            html = self._build_email(ContestBlueprintResultEmail.HEADLINE, ContestBlueprintResultEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestBlueprintResultEmail.SUBJECT.format(**ctx), html)

    def send_contest_proof_open(self, recipients: list[dict], entry: dict) -> None:
        """Send Level 3 open notification to all team members."""
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        for r in recipients:
            ctx = dict(
                app_name=self.app_name, frontend_url=self.frontend_url,
                recipient_name=r["name"], project_title=project_title,
            )
            html = self._build_email(ContestProofOpenEmail.HEADLINE, ContestProofOpenEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestProofOpenEmail.SUBJECT.format(**ctx), html)

    def send_contest_proof_result(self, recipients: list[dict], entry: dict,
                                  score: int, feedback: str, advance: bool) -> None:
        """Send Level 3 evaluation result to all team members."""
        from project_contest_schemas import SCORE_THRESHOLDS
        threshold = SCORE_THRESHOLDS["demo"]
        emoji, label, color, bg = self._contest_result_blocks(score, threshold, advance)
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        next_steps_block = (
            '<p style="font-size:14px;color:#4b5563;">Level 4 — <strong>Interrogation</strong> — opens in 30 days. '
            'Each team member will face a separate 3-round AI interview. Prepare individually.</p>'
        ) if advance else (
            '<p style="font-size:14px;color:#4b5563;">Thank you for participating. '
            'Use your Mock Interview credits to keep building your skills.</p>'
        )
        for r in recipients:
            ctx = dict(
                app_name=self.app_name, frontend_url=self.frontend_url,
                recipient_name=r["name"], project_title=project_title,
                score=score, result_emoji=emoji, result_label=label,
                result_color=color, result_bg=bg, feedback=feedback,
                next_steps_block=next_steps_block,
            )
            html = self._build_email(ContestProofResultEmail.HEADLINE, ContestProofResultEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestProofResultEmail.SUBJECT.format(**ctx), html)

    def send_contest_interview_scheduled(self, recipient: dict, entry: dict,
                                         participant_role: str) -> None:
        """Send Level 4 interview ready notification to ONE participant."""
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        ctx = dict(
            app_name=self.app_name, frontend_url=self.frontend_url,
            recipient_name=recipient["name"], project_title=project_title,
            participant_role=participant_role,
        )
        html = self._build_email(ContestInterviewScheduledEmail.HEADLINE, ContestInterviewScheduledEmail.BODY.format(**ctx))
        self.send_email(recipient["email"], ContestInterviewScheduledEmail.SUBJECT.format(**ctx), html)

    def send_contest_interview_complete(self, recipients: list[dict], entry: dict,
                                        team_score: int, advance: bool,
                                        personal_feedbacks: dict) -> None:
        """Send Level 4 team result to all members. personal_feedbacks: {email: feedback_str}"""
        from project_contest_schemas import SCORE_THRESHOLDS
        threshold = SCORE_THRESHOLDS["interview"]
        emoji, label, color, bg = self._contest_result_blocks(team_score, threshold, advance)
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        next_steps_block = (
            '<p style="font-size:14px;color:#4b5563;">Your team is now a <strong>Finalist</strong>! '
            'Final results and winner announcement coming soon.</p>'
        ) if advance else (
            '<p style="font-size:14px;color:#4b5563;">Thank you for participating. '
            'Your detailed journey report is available in your dashboard.</p>'
        )
        for r in recipients:
            personal_fb = personal_feedbacks.get(r["email"], "See your full report in the dashboard.")
            ctx = dict(
                app_name=self.app_name, frontend_url=self.frontend_url,
                recipient_name=r["name"], project_title=project_title,
                team_score=team_score, result_emoji=emoji, result_label=label,
                result_color=color, result_bg=bg,
                personal_feedback=personal_fb, next_steps_block=next_steps_block,
            )
            html = self._build_email(ContestInterviewCompleteEmail.HEADLINE, ContestInterviewCompleteEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestInterviewCompleteEmail.SUBJECT.format(**ctx), html)

    def send_contest_winner(self, recipients: list[dict], entry: dict) -> None:
        """Send winner announcement to all team members."""
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        for r in recipients:
            ctx = dict(
                app_name=self.app_name, frontend_url=self.frontend_url,
                recipient_name=r["name"], project_title=project_title,
                score_l1=entry.get("idea_quality_score", 0),
                score_l2=entry.get("blueprint_score", 0),
                score_l3=entry.get("demo_score", 0),
                score_l4=entry.get("team_interview_score", 0),
                composite_score=round(entry.get("composite_score", 0), 1),
            )
            html = self._build_email(ContestWinnerEmail.HEADLINE, ContestWinnerEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestWinnerEmail.SUBJECT.format(**ctx), html)

    def send_contest_eliminated(self, recipients: list[dict], entry: dict,
                                level_name: str, score: int, threshold: int,
                                feedback: str) -> None:
        """Send elimination notice to all team members."""
        project_title = entry.get("refined_title") or entry.get("raw_project_name", "")
        for r in recipients:
            ctx = dict(
                app_name=self.app_name, frontend_url=self.frontend_url,
                recipient_name=r["name"], project_title=project_title,
                level_name=level_name, score=score, threshold=threshold, feedback=feedback,
            )
            html = self._build_email(ContestEliminatedEmail.HEADLINE, ContestEliminatedEmail.BODY.format(**ctx))
            self.send_email(r["email"], ContestEliminatedEmail.SUBJECT.format(**ctx), html)


email_service = EmailService()
