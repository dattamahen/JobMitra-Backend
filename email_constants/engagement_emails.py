"""
Email templates for engagement campaigns.
Tone: informative, helpful, trust-first. No urgency pressure, no superlatives.
"""


class ProfileNudgeEmail:
    SUBJECT = "Your JobMouka profile is {completion_pct}% complete"
    HEADLINE = "A few more details could help recruiters find you"
    BODY = """
    <p>Hi {first_name},</p>
    <p>Your JobMouka profile is currently <strong>{completion_pct}% complete</strong>.</p>
    <p>Recruiters on the platform filter candidates by profile completeness. The sections
    listed below are commonly used in those filters:</p>
    <ul class="feature-list">
      {missing_sections_html}
    </ul>
    <p>Adding these details takes a few minutes and makes your profile visible to a wider
    range of job postings.</p>
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard/profile" class="btn">Complete your profile</a>
    </div>
    <hr class="divider"/>
    <p class="note">You are receiving this because you have an active JobMouka account.
    To stop receiving profile reminders, update your notification preferences in Settings.</p>
    """


class MockInterviewNudgeEmail:
    SUBJECT = "Your mock interview practice — a quick note"
    HEADLINE = "It has been a while since your last mock interview"
    BODY = """
    <p>Hi {first_name},</p>
    <p>It has been <strong>{days_since_last} days</strong> since your last mock interview
    session on JobMouka.</p>
    <p>Regular practice helps you get comfortable with the format and pacing of real
    interviews. Even a single session every few weeks can make a noticeable difference
    in how you respond under pressure.</p>
    <p>Your account has mock interview credits available. You can start a session whenever
    it suits you — no scheduling required.</p>
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard/mock-interviews" class="btn">Start a mock interview</a>
    </div>
    <hr class="divider"/>
    <p class="note">To stop receiving these reminders, update your notification preferences
    in Settings.</p>
    """


class ProjectContestNudgeEmail:
    SUBJECT = "JobMouka Project Contest — open for freshers"
    HEADLINE = "The JobMouka Project Contest is open"
    BODY = """
    <p>Hi {first_name},</p>
    <p>The JobMouka Project Contest is currently open for entries. It is designed for
    freshers and early-career candidates who want to demonstrate their skills through
    a real project.</p>
    <p><strong>How it works:</strong></p>
    <ul class="feature-list">
      <li>Submit your project idea (solo or as a team of up to 4)</li>
      <li>Progress through four evaluation levels: Spark, Blueprint, Proof, and Interrogation</li>
      <li>Top teams are eligible for a ₹25,000 prize</li>
    </ul>
    <p>There is no entry fee. You can submit an existing project or start a new one.</p>
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard/project-contest" class="btn">View contest details</a>
    </div>
    <hr class="divider"/>
    <p class="note">To stop receiving contest updates, update your notification preferences
    in Settings.</p>
    """


class JobDigestEmail:
    SUBJECT = "{job_count} jobs on JobMouka this week"
    HEADLINE = "Jobs posted this week on JobMouka"
    BODY = """
    <p>Hi {first_name},</p>
    <p>Here are <strong>{job_count} jobs</strong> posted on JobMouka in the last 7 days:</p>
    {job_rows_html}
    <div class="btn-wrap">
      <a href="{frontend_url}/dashboard/job-search" class="btn">Browse all jobs</a>
    </div>
    <hr class="divider"/>
    <p class="note">To stop receiving the weekly job digest, update your notification
    preferences in Settings.</p>
    """
