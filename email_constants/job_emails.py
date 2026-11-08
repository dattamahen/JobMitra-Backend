"""Internal job market email templates."""


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
