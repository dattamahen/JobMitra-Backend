"""
Email content constants — subjects, headlines, and body templates.

All user-facing copy lives here so it can be reviewed, updated, or
A/B-tested without touching service logic.

Template variables use Python str.format() named placeholders:
  {first_name}, {last_name}, {user_email}, {app_name}, {frontend_url}, etc.
"""

from email_constants.auth_emails import (
    WelcomeEmail,
    PasswordResetEmail,
    VerificationEmail,
    AuthFailureEmail,
)
from email_constants.admin_emails import (
    NewUserAdminEmail,
    CvDownloadAdminEmail,
    CvDownloadUserNudgeEmail,
)
from email_constants.job_emails import (
    InternalJobAppliedPosterEmail,
    InternalJobAppliedCandidateEmail,
)
from email_constants.contest_emails import (
    ContestSubmissionAckEmail,
    ContestMemberOtpEmail,
    ContestTeamInviteNewUserEmail,
    ContestTeamInviteExistingUserEmail,
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

__all__ = [
    "WelcomeEmail",
    "PasswordResetEmail",
    "VerificationEmail",
    "AuthFailureEmail",
    "NewUserAdminEmail",
    "CvDownloadAdminEmail",
    "CvDownloadUserNudgeEmail",
    "InternalJobAppliedPosterEmail",
    "InternalJobAppliedCandidateEmail",
    "ContestSubmissionAckEmail",
    "ContestMemberOtpEmail",
    "ContestTeamInviteNewUserEmail",
    "ContestTeamInviteExistingUserEmail",
    "ContestSparkConfirmedEmail",
    "ContestSparkConfirmedNewUserEmail",
    "ContestBlueprintOpenEmail",
    "ContestBlueprintResultEmail",
    "ContestProofOpenEmail",
    "ContestProofResultEmail",
    "ContestInterviewScheduledEmail",
    "ContestInterviewCompleteEmail",
    "ContestWinnerEmail",
    "ContestEliminatedEmail",
]
