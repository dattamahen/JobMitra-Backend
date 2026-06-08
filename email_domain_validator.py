"""
Email Domain Validation
Blocks public email providers for HR/Recruiter registration.
Only company/corporate email domains are allowed.
"""

# Public email domains that are NOT allowed for HR registration
PUBLIC_EMAIL_DOMAINS = frozenset([
    # Google
    "gmail.com", "googlemail.com",
    # Microsoft
    "outlook.com", "hotmail.com", "live.com", "msn.com", "outlook.in",
    # Yahoo
    "yahoo.com", "yahoo.in", "yahoo.co.in", "ymail.com", "rocketmail.com",
    # Apple
    "icloud.com", "me.com", "mac.com",
    # Others
    "protonmail.com", "proton.me", "tutanota.com", "zoho.com",
    "aol.com", "mail.com", "gmx.com", "gmx.net",
    "rediffmail.com", "rediff.com",
    "yandex.com", "yandex.ru",
    "mail.ru", "inbox.com",
    "fastmail.com", "hushmail.com",
    # Temporary/disposable
    "tempmail.com", "throwaway.email", "guerrillamail.com",
    "mailinator.com", "sharklasers.com", "10minutemail.com",
])


def is_company_email(email: str) -> bool:
    """Check if email belongs to a company domain (not public provider)."""
    if not email or "@" not in email:
        return False
    domain = email.split("@")[1].lower().strip()
    return domain not in PUBLIC_EMAIL_DOMAINS


def get_email_domain(email: str) -> str:
    """Extract domain from email."""
    if not email or "@" not in email:
        return ""
    return email.split("@")[1].lower().strip()
