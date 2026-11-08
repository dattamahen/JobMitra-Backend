"""Project Contest email templates."""


class ContestSubmissionAckEmail:
    """Sent to the lead (and registered team members) immediately after POST /submit succeeds."""
    SUBJECT = "\u2705 Project '{project_title}' received \u2014 {app_name} Contest"
    HEADLINE = "Your project idea has been received! \U0001f680"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>We've received your project submission for the <strong>{app_name} Project Contest</strong>. Here's a summary:</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Idea Quality Score:</strong> {idea_quality_score}/100</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Team Size:</strong> {team_size} member(s)</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">\U0001f5fa\ufe0f What's next?</p>
    <ul class="feature-list">
      <li>Review the AI-refined version of your idea and <strong>confirm it</strong> in your dashboard</li>
      <li>Complete payment to officially activate your entry</li>
      <li>Once confirmed, Level 2 \u2014 <strong>Blueprint</strong> \u2014 opens in 30 days</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Review &amp; Confirm Your Idea</a>
    </div>
    <p class="note">Your entry is not yet active \u2014 please complete the confirmation and payment steps to lock in your spot.</p>
    """


class ContestMemberOtpEmail:
    """OTP sent to a team member email for verification before form submission."""
    SUBJECT = "\U0001f510 Your team verification code \u2014 {app_name} Project Contest"
    HEADLINE = "Team Member Verification Code"
    BODY = """
    <p>Hi,</p>
    <p><strong>{lead_name}</strong> is adding you as a team member for the <strong>{app_name} Project Contest</strong>.</p>
    <p>Use the code below to confirm your participation:</p>
    <div class="code-box"><span class="code">{otp}</span></div>
    <p class="note">\u23f0 This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
    <p style="font-size:14px;color:#4b5563;margin-top:16px;">Once your team submits the project, you'll receive a full invite email with contest details and the <strong>\u20b925,000 prize</strong> opportunity.</p>
    """


class ContestTeamInviteNewUserEmail:
    """Sent at submission time to team members who don't have a JobMouka account."""
    SUBJECT = "\U0001f3c6 Your teammate enrolled you in a contest \u2014 Win \u20b925,000 | {app_name}"
    HEADLINE = "You've been invited to a \u20b925,000 contest! \U0001f389"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Your teammate <strong>{lead_name}</strong> has enrolled you as a team member for the project <strong>{project_title}</strong> in the <strong>{app_name} Project Contest</strong>.</p>

    <div style="background:linear-gradient(135deg,#fef9c3,#fef08a);border:2px solid #ca8a04;border-radius:12px;padding:20px 24px;margin:20px 0;text-align:center;">
      <p style="font-size:28px;font-weight:800;color:#92400e;margin:0;">\U0001f3c6 \u20b925,000 Cash Prize</p>
      <p style="font-size:14px;color:#78350f;margin-top:6px;">The winning team takes home \u20b925,000. Your team is already in!</p>
    </div>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">YOUR PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Team Lead:</strong> {lead_name}</p>
    </div>

    <p>Create your free <strong>{app_name}</strong> account to participate and claim your benefits:</p>
    <ul class="feature-list">
      <li>Participate in the <strong>Level 4 AI Interview</strong> round (mandatory for all team members)</li>
      <li>Claim <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong> added to your account</li>
      <li>Track your team's contest progress in real time</li>
      <li>Build your career profile \u2014 AI resume builder, job search, mock interviews</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/login" class="btn">Create Your Free Account</a>
    </div>
    <p class="note">The contest has 5 levels. Your team has already cleared Level 1. Don't miss out on the \u20b925,000 prize!</p>
    """


class ContestTeamInviteExistingUserEmail:
    """Sent at submission time to team members who already have a JobMouka account."""
    SUBJECT = "\U0001f3c6 {lead_name} added you to a contest entry \u2014 '{project_title}' | {app_name}"
    HEADLINE = "You've been added to a contest team! \U0001f389"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Your teammate <strong>{lead_name}</strong> has added you as a team member for the project <strong>{project_title}</strong> in the <strong>{app_name} Project Contest</strong>.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">YOUR PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Team Lead:</strong> {lead_name}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Team Size:</strong> {team_size} member(s)</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">\U0001f4cb Project Summary</p>
    <p style="font-size:14px;color:#4b5563;background:#f9fafb;border-radius:8px;padding:12px 16px;">{project_summary}</p>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">\U0001f5fa\ufe0f Contest Levels</p>
    <ul class="feature-list">
      <li><strong>Level 1 \u2705 Spark</strong> \u2014 Idea submitted (pending payment confirmation)</li>
      <li><strong>Level 2 \u2014 Blueprint</strong> \u2014 AI-generated questionnaire about your project</li>
      <li><strong>Level 3 \u2014 Proof</strong> \u2014 Demo video and GitHub repository</li>
      <li><strong>Level 4 \u2014 Interrogation</strong> \u2014 Individual AI interview for each team member</li>
      <li><strong>Level 5 \u2014 Verdict</strong> \u2014 Top project wins <strong>\u20b925,000 cash prize</strong></li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View in Dashboard</a>
    </div>
    <p class="note">Once payment is confirmed by your team lead, your entry will be officially live and credits will be added to your account.</p>
    """


class ContestSparkConfirmedEmail:
    """Sent to ALL team members when payment is confirmed and entry is live."""
    SUBJECT = "\U0001f3c6 You're in! Project '{project_title}' is officially entered \u2014 {app_name} Contest"
    HEADLINE = "Your contest entry is confirmed! \U0001f389"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Great news \u2014 <strong>{lead_name}</strong>'s project has been officially entered into the <strong>{app_name} Project Contest</strong>.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Team Size:</strong> {team_size} member(s)</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:24px 0 10px;">\U0001f5fa\ufe0f What happens next?</p>
    <ul class="feature-list">
      <li><strong>Level 1 \u2705 Spark</strong> \u2014 Your idea is confirmed and entry is live</li>
      <li><strong>Level 2 \u2014 Blueprint</strong> opens in <strong>30 days</strong>. You'll answer a custom AI-generated questionnaire about your project</li>
      <li><strong>Level 3 \u2014 Proof</strong> \u2014 Submit your working demo video and GitHub repo</li>
      <li><strong>Level 4 \u2014 Interrogation</strong> \u2014 Each team member faces a 3-round AI interview</li>
      <li><strong>Level 5 \u2014 Verdict</strong> \u2014 Top project wins <strong>\u20b925,000</strong></li>
    </ul>

    <p>\u2705 You've also received <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong> added to your account.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">View Your Entry</a>
    </div>
    <p class="note">Keep an eye on your inbox \u2014 we'll notify you when Level 2 opens.</p>
    """


class ContestSparkConfirmedNewUserEmail:
    """Sent to team members who don't have an account yet \u2014 after payment confirmed."""
    SUBJECT = "\U0001f3c6 You've been added to '{project_title}' \u2014 Join {app_name} to claim your benefits"
    HEADLINE = "Your team's entry is confirmed! Create your account \U0001f389"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p><strong>{lead_name}</strong>'s team entry for <strong>{project_title}</strong> is now officially live in the <strong>{app_name} Project Contest</strong>.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">PROJECT</p>
      <p style="font-size:18px;font-weight:700;color:#1a1a2e;margin-bottom:4px;">{project_title}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Entry ID:</strong> {entry_id}</p>
      <p style="font-size:13px;color:#4b5563;"><strong>Category:</strong> {category}</p>
    </div>

    <p>\U0001f381 Create your free account to:</p>
    <ul class="feature-list">
      <li>Claim <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong> added to your account</li>
      <li>Track your team's contest progress</li>
      <li>Participate in the Level 4 AI interview round (required to win)</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/login" class="btn">Create Your Account</a>
    </div>
    <p class="note">The contest has 5 levels \u2014 the top project wins <strong>\u20b925,000</strong>. Don't miss out!</p>
    """


class ContestBlueprintOpenEmail:
    """Sent to ALL team members when Level 2 opens."""
    SUBJECT = "\U0001f4cb Level 2 is open \u2014 Blueprint questionnaire ready for '{project_title}'"
    HEADLINE = "Level 2 \u2014 Blueprint is now open \U0001f4cb"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Level 2 of the <strong>{app_name} Project Contest</strong> is now open for your project <strong>{project_title}</strong>.</p>

    <div style="background:#fefce8;border-left:4px solid #ca8a04;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:14px;font-weight:700;color:#92400e;">\u23f0 Deadline: 30 days from today</p>
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

    <p>These are not generic questions \u2014 every question references your actual project. Answer with depth and specificity.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Answer Blueprint Questions</a>
    </div>
    <p class="note">Minimum score to advance: <strong>65/100</strong>. Detailed AI feedback will be provided regardless of outcome.</p>
    """


class ContestBlueprintResultEmail:
    """Sent to ALL team members after blueprint evaluation."""
    SUBJECT = "{result_emoji} Blueprint result for '{project_title}' \u2014 Score: {score}/100"
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
    SUBJECT = "\U0001f3ac Level 3 is open \u2014 Submit your demo for '{project_title}'"
    HEADLINE = "Level 3 \u2014 Proof of Work is now open \U0001f3ac"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Congratulations on passing Level 2! Level 3 \u2014 <strong>Proof</strong> \u2014 is now open for <strong>{project_title}</strong>.</p>

    <div style="background:#fefce8;border-left:4px solid #ca8a04;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:14px;font-weight:700;color:#92400e;">\u23f0 Deadline: 30 days from today</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">What you need to submit:</p>
    <ul class="feature-list">
      <li><strong>YouTube demo video</strong> \u2014 A working demo of your project (minimum 3 minutes). Show the problem, the solution, and the core features in action</li>
      <li><strong>GitHub repository URL</strong> \u2014 Your actual codebase with a proper README</li>
      <li><strong>Live demo URL</strong> (optional but recommended)</li>
    </ul>

    <p style="font-size:14px;color:#4b5563;">The AI will evaluate your video, GitHub activity, and demo quality. A slideshow is not a demo \u2014 show it working.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Submit Your Demo</a>
    </div>
    <p class="note">Minimum score to advance: <strong>70/100</strong>.</p>
    """


class ContestProofResultEmail:
    """Sent to ALL team members after demo evaluation."""
    SUBJECT = "{result_emoji} Demo evaluation result for '{project_title}' \u2014 Score: {score}/100"
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
    SUBJECT = "\U0001f3a4 Your Level 4 interview is ready \u2014 '{project_title}'"
    HEADLINE = "Level 4 \u2014 Your AI Interview is Ready \U0001f3a4"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>Level 4 \u2014 <strong>Interrogation</strong> \u2014 is now open for <strong>{project_title}</strong>. This is your personal interview.</p>

    <div style="background:#f5f3ff;border-left:4px solid #4831af;border-radius:8px;padding:16px 20px;margin:20px 0">
      <p style="font-size:13px;color:#6b7280;margin-bottom:4px;">YOUR ROLE IN THE PROJECT</p>
      <p style="font-size:16px;font-weight:700;color:#1a1a2e;">{participant_role}</p>
      <p style="font-size:13px;color:#4b5563;margin-top:8px;"><strong>3 rounds</strong> \u00d7 <strong>8 questions</strong> each</p>
    </div>

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">The 3 rounds:</p>
    <ul class="feature-list">
      <li><strong>Round 1 \u2014 Conceptual Depth:</strong> Do you understand the foundations behind your project?</li>
      <li><strong>Round 2 \u2014 Execution &amp; Decisions:</strong> Why did you build it this way? What broke?</li>
      <li><strong>Round 3 \u2014 Stress &amp; Edge Cases:</strong> Failure modes, scale, security, pivot questions</li>
    </ul>

    <p style="font-size:14px;color:#dc2626;font-weight:600;">\u26a0\ufe0f Important: Each team member is interviewed separately. Your answers must reflect your own understanding and contribution.</p>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Start My Interview</a>
    </div>
    <p class="note">Deadline: <strong>30 days</strong>. Minimum team score to advance: <strong>72/100</strong>.</p>
    """


class ContestInterviewCompleteEmail:
    """Sent to ALL team members after all interviews are evaluated."""
    SUBJECT = "\U0001f4ca Interview results for '{project_title}' \u2014 Team Score: {team_score}/100"
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
    SUBJECT = "\U0001f3c6 YOU WON! '{project_title}' wins the {app_name} Project Contest \u2014 \u20b925,000!"
    HEADLINE = "\U0001f3c6 Congratulations \u2014 You Won!"
    BODY = """
    <p>Hi <strong>{recipient_name}</strong>,</p>
    <p>We are thrilled to announce that <strong>{project_title}</strong> has won the <strong>{app_name} Project Contest</strong>!</p>

    <div style="background:linear-gradient(135deg,#fef9c3,#fef08a);border:2px solid #ca8a04;border-radius:12px;padding:24px;margin:20px 0;text-align:center;">
      <p style="font-size:40px;margin:0;">\U0001f3c6</p>
      <p style="font-size:24px;font-weight:800;color:#92400e;margin:8px 0;">\u20b925,000</p>
      <p style="font-size:14px;color:#78350f;">First Prize \u2014 {app_name} Project Contest</p>
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
    SUBJECT = "\U0001f4ca Contest update for '{project_title}' \u2014 {level_name} result"
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

    <p style="font-size:15px;font-weight:600;color:#1a1a2e;margin:20px 0 10px;">Keep building \U0001f680</p>
    <ul class="feature-list">
      <li>Use your <strong>Mock Interview</strong> credits to sharpen your technical skills</li>
      <li>Download your CV and apply to jobs on JobMouka</li>
      <li>The next contest round will be announced soon \u2014 come back stronger</li>
    </ul>

    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard" class="btn">Go to Dashboard</a>
    </div>
    """
