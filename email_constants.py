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


# ── Project Contest Emails ──────────────────────────────────

class ContestSparkConfirmedEmail:
    """Sent to ALL team members when payment is confirmed and entry is live."""
    SUBJECT = "🏆 You're in! Project '{project_title}' is officially entered — {app_name} Contest"
    HEADLINE = "Your contest entry is confirmed! 🎉"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Great news — <strong>{lead_name}</strong>'s project has been officially entered into the <strong>{app_name} Project Contest</strong>.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Team Size:</strong> {team_size} member(s)</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:24px 0 10px;">🗺️ What happens next?</p>
    <ul class="feature-list">
      <li><strong>Level 1 ✅ Spark</strong> — Your idea is confirmed and entry is live</li>
      <li><strong>Level 2 — Blueprint</strong> opens in <strong>30 days</strong>. You'll answer a custom AI-generated questionnaire about your project</li>
      <li><strong>Level 3 — Proof</strong> — Submit your working demo video and GitHub repo</li>
      <li><strong>Level 4 — Interrogation</strong> — Each team member faces a 3-round AI interview</li>
      <li><strong>Level 5 — Verdict</strong> — Top project wins <strong>₹25,000</strong></li>
    </ul>

    <p>✅ You've also received <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong> added to your account.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View Your Entry</a>
    </div>
    <p class="note">Keep an eye on your inbox — we'll notify you when Level 2 opens.</p>
    """


class ContestSparkConfirmedNewUserEmail:
    """Sent to team members who don't have an account yet."""
    SUBJECT = "🏆 You've been added to '{project_title}' — Join {app_name} to claim your benefits"
    HEADLINE = "You're part of a contest team! 🎉"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p><strong>{lead_name}</strong> has added you as a team member for the project <strong>{project_title}</strong> in the <strong>{app_name} Project Contest</strong>.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
    </div>

    <p>🎁 Create your free account to:</p>
    <ul class="feature-list">
      <li>Claim <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong></li>
      <li>Track your team's contest progress</li>
      <li>Participate in the Level 4 AI interview round</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/login" class="btn">Create Your Account</a>
    </div>
    <p class="note">The contest has 5 levels — the top project wins ₹25,000. Don't miss out!</p>
    """


class ContestBlueprintOpenEmail:
    """Sent to ALL team members when Level 2 opens."""
    SUBJECT = "📋 Level 2 is open — Blueprint questionnaire ready for '{project_title}'"
    HEADLINE = "Level 2 — Blueprint is now open 📋"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Level 2 of the <strong>{app_name} Project Contest</strong> is now open for your project <strong>{project_title}</strong>.</p>

    <div style="background:#fefce8;border-left:4px solid #ca8a04;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:14px;font-weight:700;color:#92400e;">⏰ Deadline: 30 days from today</p>
      <p style="font-size:13px;color:#78350f;margin-top:4px;">Your team must submit all 12 answers before the deadline to advance to Level 3.</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">What is the Blueprint round?</p>
    <p>Our AI has generated a <strong>custom 12-question questionnaire</strong> tailored specifically to your project. The questions cover:</p>
    <ul class="feature-list">
      <li>Architecture &amp; Technical Design decisions</li>
      <li>Problem-Solution fit and why your approach works</li>
      <li>Team execution and individual role contributions</li>
      <li>Scalability and real-world readiness</li>
    </ul>

    <p>These are not generic questions — every question references your actual project. Answer with depth and specificity.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Answer Blueprint Questions</a>
    </div>
    <p class="note">Minimum score to advance: <strong>65/100</strong>. Detailed AI feedback will be provided regardless of outcome.</p>
    """


class ContestBlueprintResultEmail:
    """Sent to ALL team members after blueprint evaluation."""
    SUBJECT = "{result_emoji} Blueprint result for '{project_title}' — Score: {score}/100"
    HEADLINE = "Blueprint Evaluation Complete"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>The AI evaluation of your Blueprint submission for <strong>{project_title}</strong> is complete.</p>

    <div style="background:{result_bg};border-left:4px solid {result_color};border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">BLUEPRINT SCORE</p>
      <p style="font-size:32px;font-weight:800;color:{result_color};margin:0;">{score}<span style="font-size:16px;font-weight:400;">/100</span></p>
      <p style="font-size:14px;font-weight:600;color:{result_color};margin-top:4px;">{result_label}</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">AI Feedback</p>
    <p style="font-size:14px;color:#4b5563;background:#f9fafb;border-radius:8px;padding:12px 16px;">{feedback}</p>

    {next_steps_block}

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View Full Results</a>
    </div>
    """


class ContestProofOpenEmail:
    """Sent to ALL team members when Level 3 opens."""
    SUBJECT = "🎬 Level 3 is open — Submit your demo for '{project_title}'"
    HEADLINE = "Level 3 — Proof of Work is now open 🎬"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Congratulations on passing Level 2! Level 3 — <strong>Proof</strong> — is now open for <strong>{project_title}</strong>.</p>

    <div style="background:#fefce8;border-left:4px solid #ca8a04;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:14px;font-weight:700;color:#92400e;">⏰ Deadline: 30 days from today</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">What you need to submit:</p>
    <ul class="feature-list">
      <li><strong>YouTube demo video</strong> — A working demo of your project (minimum 3 minutes). Show the problem, the solution, and the core features in action</li>
      <li><strong>GitHub repository URL</strong> — Your actual codebase with a proper README</li>
      <li><strong>Live demo URL</strong> (optional but recommended)</li>
    </ul>

    <p style="font-size:14px;color:#4b5563;">The AI will evaluate your video, GitHub activity, and demo quality. A slideshow is not a demo — show it working.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Submit Your Demo</a>
    </div>
    <p class="note">Minimum score to advance: <strong>70/100</strong>.</p>
    """


class ContestProofResultEmail:
    """Sent to ALL team members after demo evaluation."""
    SUBJECT = "{result_emoji} Demo evaluation result for '{project_title}' — Score: {score}/100"
    HEADLINE = "Demo Evaluation Complete"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>The AI evaluation of your demo submission for <strong>{project_title}</strong> is complete.</p>

    <div style="background:{result_bg};border-left:4px solid {result_color};border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">DEMO SCORE</p>
      <p style="font-size:32px;font-weight:800;color:{result_color};margin:0;">{score}<span style="font-size:16px;font-weight:400;">/100</span></p>
      <p style="font-size:14px;font-weight:600;color:{result_color};margin-top:4px;">{result_label}</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">AI Feedback</p>
    <p style="font-size:14px;color:#4b5563;background:#f9fafb;border-radius:8px;padding:12px 16px;">{feedback}</p>

    {next_steps_block}

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View Full Results</a>
    </div>
    """


class ContestInterviewScheduledEmail:
    """Sent to EACH team member individually when their interview is ready."""
    SUBJECT = "🎤 Your Level 4 interview is ready — '{project_title}'"
    HEADLINE = "Level 4 — Your AI Interview is Ready 🎤"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Level 4 — <strong>Interrogation</strong> — is now open for <strong>{project_title}</strong>. This is your personal interview.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">YOUR ROLE IN THE PROJECT</p>
      <p style="font-size:16px;font-weight:700;color:#1a1a2e;">{participant_role}</p>
      <p style="font-size:13px;color:#4b5563;margin-top:8px;"><strong>3 rounds</strong> × <strong>8 questions</strong> each</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">The 3 rounds:</p>
    <ul class="feature-list">
      <li><strong>Round 1 — Conceptual Depth:</strong> Do you understand the foundations behind your project?</li>
      <li><strong>Round 2 — Execution &amp; Decisions:</strong> Why did you build it this way? What broke?</li>
      <li><strong>Round 3 — Stress &amp; Edge Cases:</strong> Failure modes, scale, security, pivot questions</li>
    </ul>

    <p style="font-size:14px;color:#dc2626;font-weight:600;">⚠️ Important: Each team member is interviewed separately. Your answers must reflect your own understanding and contribution.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Start My Interview</a>
    </div>
    <p class="note">Deadline: <strong>30 days</strong>. Minimum team score to advance: <strong>72/100</strong>.</p>
    """


class ContestInterviewCompleteEmail:
    """Sent to ALL team members after all interviews are evaluated."""
    SUBJECT = "📊 Interview results for '{project_title}' — Team Score: {team_score}/100"
    HEADLINE = "Level 4 Interview Results"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>All interviews for <strong>{project_title}</strong> have been evaluated. Here are the results.</p>

    <div style="background:{result_bg};border-left:4px solid {result_color};border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">TEAM INTERVIEW SCORE</p>
      <p style="font-size:32px;font-weight:800;color:{result_color};margin:0;">{team_score}<span style="font-size:16px;font-weight:400;">/100</span></p>
      <p style="font-size:14px;font-weight:600;color:{result_color};margin-top:4px;">{result_label}</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">Your Personal Score</p>
    <p style="font-size:14px;color:#4b5563;background:#f9fafb;border-radius:8px;padding:12px 16px;">{personal_feedback}</p>

    {next_steps_block}

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View Full Results</a>
    </div>
    """


class ContestWinnerEmail:
    """Sent to ALL team members of the winning project."""
    SUBJECT = "🏆 YOU WON! '{project_title}' wins the {app_name} Project Contest — ₹25,000!"
    HEADLINE = "🏆 Congratulations — You Won!"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>We are thrilled to announce that <strong>{project_title}</strong> has won the <strong>{app_name} Project Contest</strong>!</p>

    <div style="background:linear-gradient(135deg,#fef9c3,#fef08a);border:2px solid #ca8a04;border-radius:12px;padding:24px;margin:20px 0;text-align:center;">
      <p style="font-size:40px;margin:0;">🏆</p>
      <p style="font-size:24px;font-weight:800;color:#92400e;margin:8px 0;">₹25,000</p>
      <p style="font-size:14px;color:#78350f;">First Prize — {app_name} Project Contest</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">Your composite score:</p>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <tr style="background:#f9fafb;"><td style="padding:8px 12px;color:#6b7280;">Idea Quality (L1)</td><td style="padding:8px 12px;font-weight:600;">{score_l1}/100</td></tr>
      <tr><td style="padding:8px 12px;color:#6b7280;">Blueprint (L2)</td><td style="padding:8px 12px;font-weight:600;">{score_l2}/100</td></tr>
      <tr style="background:#f9fafb;"><td style="padding:8px 12px;color:#6b7280;">Demo (L3)</td><td style="padding:8px 12px;font-weight:600;">{score_l3}/100</td></tr>
      <tr><td style="padding:8px 12px;color:#6b7280;">Interview (L4)</td><td style="padding:8px 12px;font-weight:600;">{score_l4}/100</td></tr>
      <tr style="background:#f5f3ff;"><td style="padding:10px 12px;color:#4831af;font-weight:700;">Composite Score</td><td style="padding:10px 12px;color:#4831af;font-weight:800;font-size:16px;">{composite_score}/100</td></tr>
    </table>

    <p style="margin-top:20px;">A <strong>Winner badge</strong> has been added to your JobMouka profile. The prize disbursement team will contact you within 7 business days.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View Your Profile</a>
    </div>
    """


class ContestEliminatedEmail:
    """Sent to ALL team members when eliminated at any level."""
    SUBJECT = "📊 Contest update for '{project_title}' — {level_name} result"
    HEADLINE = "Contest Evaluation Result"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Thank you for participating in the <strong>{app_name} Project Contest</strong> with <strong>{project_title}</strong>.</p>

    <div style="background:#fef2f2;border-left:4px solid #dc2626;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:14px;font-weight:700;color:#991b1b;">Your team did not advance past {level_name}</p>
      <p style="font-size:13px;color:#7f1d1d;margin-top:4px;">Score: <strong>{score}/100</strong> (minimum required: {threshold}/100)</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 8px;">AI Feedback</p>
    <p style="font-size:14px;color:#4b5563;background:#f9fafb;border-radius:8px;padding:12px 16px;">{feedback}</p>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">Keep building 🚀</p>
    <ul class="feature-list">
      <li>Use your <strong>Mock Interview</strong> credits to sharpen your technical skills</li>
      <li>Download your CV and apply to jobs on JobMouka</li>
      <li>The next contest round will be announced soon — come back stronger</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Go to Dashboard</a>
    </div>
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
