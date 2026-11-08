"""Admin notification and CV download email templates."""


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
