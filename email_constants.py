"""
Email content constants — subjects, headlines, and body templates.

All user-facing copy lives here so it can be reviewed, updated, or
A/B-tested without touching service logic.

Template variables use Python str.format() named placeholders:
  {first_name}, {last_name}, {user_email}, {app_name}, {frontend_url}, etc.
"""


class WelcomeEmail:
    SUBJECT = "Welcome to {app_name} \U0001f389"
    HEADLINE = "Welcome aboard! \U0001f389"
    BODY = """
    <p>Hi <strong>{user_name}</strong>,</p>
    <p>Welcome to <strong>{app_name}</strong> — your AI-powered career platform. We're thrilled to have you on board!</p>
    <p>Here's what you can do right now:</p>
    <ul class="feature-list">
      <li>Build an ATS-optimized resume with AI</li>
      <li>Search and apply to 10,000+ job listings</li>
      <li>Practice mock interviews with AI feedback</li>
      <li>Get match analysis for every job you apply to</li>
    </ul>
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Go to Dashboard</a>
    </div>
    <p class="note">If you have any questions, just reply to this email — we're happy to help.</p>
    """


class PasswordResetEmail:
    SUBJECT = "Reset Your {app_name} Password"
    HEADLINE = "Password Reset Request"
    BODY = """
    <p>Hi <strong>{user_name}</strong>,</p>
    <p>We received a request to reset your <strong>{app_name}</strong> password. Click the button below to set a new one:</p>
    <div class="btn-wrap">
      <a href="{reset_link}" class="btn">Reset My Password</a>
    </div>
    <p>Or copy and paste this link into your browser:</p>
    <div class="link-box">{reset_link}</div>
    <hr class="divider"/>
    <p class="note">&#9201; This link expires in <strong>1 hour</strong>.</p>
    <p class="note">If you didn't request this, you can safely ignore this email — your password won't change.</p>
    """


class VerificationEmail:
    SUBJECT = "Verify Your {app_name} HR Account"
    HEADLINE = "Verify Your HR Account"
    BODY = """
    <p>Hi <strong>{user_name}</strong>,</p>
    <p>Thank you for registering as an HR / Recruiter on <strong>{app_name}</strong>.</p>
    <p>To activate your account and start posting jobs, please verify your email:</p>
    <div class="btn-wrap">
      <a href="{verify_link}" class="btn">Verify My Account</a>
    </div>
    <p style="text-align:center;font-size:14px;color:#6b7280;">Or use this one-time code:</p>
    <div class="code-box"><span class="code">{code}</span></div>
    <p>Or copy and paste this link:</p>
    <div class="link-box">{verify_link}</div>
    <hr class="divider"/>
    <p class="note">&#9201; This link expires in <strong>24 hours</strong>.</p>
    <p style="font-size:14px;color:#4b5563;margin-top:16px;">Once verified, you'll be able to:</p>
    <ul class="feature-list">
      <li>Post job openings</li>
      <li>View and manage applications</li>
      <li>Access candidate profiles</li>
    </ul>
    """


class AuthFailureEmail:
    # To user
    USER_SUBJECT = "{app_name} \u2014 {type_label} Failed"
    USER_HEADLINE = "{type_label} Failed"
    USER_BODY = """
    <p>Hi{name_part},</p>
    <p>We noticed a failed <strong>{type_label}</strong> attempt on your account.</p>
    <p>If this was you, please try again or contact support. If it wasn't you, your account is safe — no action is needed.</p>
    <div class="btn-wrap">
      <a href="{frontend_url}/login" class="btn">Go to Login</a>
    </div>
    <p class="note">If you need help, reply to this email.</p>
    """
    # To admin
    ADMIN_SUBJECT = "[{app_name}] Auth Failure \u2014 {user_email}"
    ADMIN_HEADLINE = "Auth Failure Alert"
    ADMIN_BODY = """
    <p><strong>Auth Failure Alert</strong></p>
    <p><strong>Type:</strong> {type_label}</p>
    <p><strong>User Email:</strong> {user_email}</p>
    <p><strong>Name:</strong> {user_name}</p>
    <p><strong>Reason:</strong> {reason}</p>
    """


class NewUserAdminEmail:
    SUBJECT = "[{app_name}] New User Registered \u2014 {first_name} {last_name}"
    HEADLINE = "New User Registration"
    BODY = """
    <p>A new user has registered on <strong>{app_name}</strong>.</p>
    <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
      <tr><td style="padding:8px 0;color:#6b7280;width:140px;">First Name</td><td style="padding:8px 0;color:#111827;"><strong>{first_name}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">Last Name</td><td style="padding:8px 0;color:#111827;"><strong>{last_name}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">Email</td><td style="padding:8px 0;color:#4831af;"><strong>{user_email}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">Sign-up Method</td><td style="padding:8px 0;color:#111827;"><strong>{signup_method}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">User Type</td><td style="padding:8px 0;color:#111827;"><strong>{user_type}</strong></td></tr>
    </table>
    """


class CvDownloadAdminEmail:
    SUBJECT = "[{app_name}] CV Downloaded \u2014 {first_name} {last_name}"
    HEADLINE = "CV Download Activity"
    BODY = """
    <p>A candidate has successfully downloaded their CV from <strong>{app_name}</strong>.</p>
    <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
      <tr><td style="padding:8px 0;color:#6b7280;width:140px;">First Name</td><td style="padding:8px 0;color:#111827;"><strong>{first_name}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">Last Name</td><td style="padding:8px 0;color:#111827;"><strong>{last_name}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">Email</td><td style="padding:8px 0;color:#4831af;"><strong>{user_email}</strong></td></tr>
      <tr><td style="padding:8px 0;color:#6b7280;">Activity</td><td style="padding:8px 0;color:#111827;"><strong>CV Downloaded</strong></td></tr>
    </table>
    """


class CvDownloadUserNudgeEmail:
    SUBJECT = "Your CV is ready \u2014 maximise your shortlisting chances with {app_name}"
    HEADLINE = "Your CV is ready \u2014 here\u2019s what to do next \U0001f680"
    BODY = """
    <p>Hi <strong>{first_name}</strong>,</p>
    <p>Great move \u2014 your CV is ready! Now let\u2019s make sure it lands at the top of every recruiter\u2019s shortlist.</p>
    <p>Here are two powerful steps you can take right now:</p>
    <ul class="feature-list">
      <li><strong>Tailor your CV to the Job Description</strong> \u2014 Upload the JD for any role you\u2019re targeting and let our AI align your CV to the exact skills and keywords recruiters are screening for. A tailored CV dramatically improves your chances of clearing ATS filters and getting noticed.</li>
      <li><strong>Sharpen your interview skills with AI Mock Interviews</strong> \u2014 Practice role-specific questions, receive instant feedback on your answers, and walk into every interview with confidence. Candidates who practise consistently are significantly more likely to convert interviews into offers.</li>
    </ul>
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Get Started Now</a>
    </div>
    <p class="note">Your next opportunity is closer than you think \u2014 make every application count.</p>
    """


class InternalJobAppliedPosterEmail:
    SUBJECT = "\U0001f4e9 New application for \u2018{job_title}\u2019 at {company}"
    HEADLINE = "Someone just applied to your job \U0001f64c"
    BODY = """
    <p>Hi,</p>
    <p>Great news! A candidate has applied to your internal job posting on <strong>{app_name}</strong>.</p>

    <!-- Job Info -->
    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">POSITION</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:2px;">{job_title}</p>
      <p style="font-size:14px;color:#4b5563;">{company}</p>
    </div>

    <!-- Candidate Profile Snapshot -->
    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:24px 0 12px;">\U0001f464 Candidate Profile</p>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <tr style="background:#f9fafb;">
        <td style="padding:10px 14px;color:#6b7280;width:38%;border-bottom:1px solid #e5e7eb;">Full Name</td>
        <td style="padding:10px 14px;color:#111827;font-weight:600;border-bottom:1px solid #e5e7eb;">{applicant_name}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;color:#6b7280;border-bottom:1px solid #e5e7eb;">Email</td>
        <td style="padding:10px 14px;border-bottom:1px solid #e5e7eb;"><a href="mailto:{applicant_email}" style="color:#4831af;font-weight:600;">{applicant_email}</a></td>
      </tr>
      {phone_row}
      {experience_row}
      {current_role_row}
      {location_row}
      <tr style="background:#f9fafb;">
        <td style="padding:10px 14px;color:#6b7280;border-bottom:1px solid #e5e7eb;">Applied On</td>
        <td style="padding:10px 14px;color:#111827;border-bottom:1px solid #e5e7eb;">{applied_date}</td>
      </tr>
      {match_row}
    </table>

    {skills_block}

    {summary_block}

    <!-- Links -->
    {links_block}

    <hr class="divider"/>
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View in Refer &amp; Hire</a>
    </div>
    <!-- WhatsApp Share -->
    <div style="text-align:center;margin:16px 0;">
      <a href="{whatsapp_share_url}" target="_blank"
         style="display:inline-flex;align-items:center;gap:8px;background:#25D366;color:#fff;font-weight:600;font-size:14px;padding:10px 22px;border-radius:8px;text-decoration:none;">
        &#128172; Share this job on WhatsApp
      </a>
    </div>
    <p class="note">Log in to JobMouka and open <strong>Refer &amp; Hire</strong> to see all applicants for this posting.</p>
    """


class InternalJobAppliedCandidateEmail:
    SUBJECT = "\u2705 Application submitted \u2014 {job_title} at {company}"
    HEADLINE = "You\u2019re in the running! \U0001f3af"
    BODY = """
    <p>Hi <strong>{applicant_name}</strong>,</p>
    <p>Your application for <strong>{job_title}</strong> at <strong>{company}</strong> has been successfully submitted through <strong>{app_name}</strong>'s Internal Job Market.</p>

    <!-- Application Summary -->
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:20px 24px;margin:20px 0;">
      <p style="font-size:13px;font-weight:600;color:#16a34a;letter-spacing:.5px;margin-bottom:12px;">\u2705 APPLICATION CONFIRMED</p>
      <table style="width:100%;font-size:14px;border-collapse:collapse;">
        <tr><td style="padding:6px 0;color:#6b7280;width:38%;">Position</td><td style="padding:6px 0;color:#111827;font-weight:600;">{job_title}</td></tr>
        <tr><td style="padding:6px 0;color:#6b7280;">Company</td><td style="padding:6px 0;color:#111827;">{company}</td></tr>
        <tr><td style="padding:6px 0;color:#6b7280;">Applied On</td><td style="padding:6px 0;color:#111827;">{applied_date}</td></tr>
        {match_row}
      </table>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:24px 0 10px;">\U0001f4a1 What happens next?</p>
    <ul class="feature-list">
      <li>The hiring team has been notified and will review your profile</li>
      <li>They may reach out directly to your registered email</li>
      <li>Keep your profile updated to improve your chances</li>
    </ul>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:24px 0 10px;">\U0001f680 Boost your chances while you wait</p>
    <ul class="feature-list">
      <li>Practice a <strong>Mock Interview</strong> for this exact role</li>
      <li>Tailor your CV to the job description for a higher match score</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Go to Dashboard</a>
    </div>
    <p class="note">You can track all your applications under <strong>My Applications</strong> in your dashboard.</p>
    """
