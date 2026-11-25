"""
Resume Tailor Agent using Gemini AI for intelligent resume customization.
"""

import logging

logger = logging.getLogger(__name__)

import os
import json
from google import genai
from prompt_manager import prompt_manager
from api_contracts import parse_tailor_response

MODEL = "gemini-3.8-flash"


def run_resume_tailor(user_profile: dict, job_description: str) -> dict:
    """Execute resume tailoring using Gemini AI."""
    try:
        logger.debug("Starting resume tailoring with Gemini...")
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        client = genai.Client(api_key=gemini_api_key)
        
        # Extract user data
        user_data = {
            "name": f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip(),
            "email": user_profile.get('email', ''),
            "phone": user_profile.get('phone', ''),
            "location": user_profile.get('city', ''),
            "professional_summary": user_profile.get('professional_summary', ''),
            "skills": user_profile.get('skills', []),
            "work_experience": user_profile.get('work_experience', []),
            "education": user_profile.get('education', []),
            "projects": user_profile.get('projects', []),
            "certifications": user_profile.get('certifications', []),
            "overall_experience_years": user_profile.get('overall_experience_years', 0)
        }
        
        tailor_variant = prompt_manager.get_random("resume_tailoring")
        tailor_system_prompt = tailor_variant.get("system_prompt")
        
        total_exp = user_data.get("overall_experience_years", 0)

        prompt = f"""
{tailor_system_prompt}

Your task:
- Tailor a candidate's CV specifically for the provided Job Description (JD).
- Highlight the most relevant skills, experience, and achievements.
- Rewrite content to match keywords and expectations from the JD.
- Do NOT fabricate experience, companies, or skills.
- Preserve truthfulness while optimizing phrasing and structure.
- Optimize for ATS (Applicant Tracking Systems).

CRITICAL — Work Experience R&R Rules:
- For EACH work experience entry, generate EXACTLY 4-5 bullet points in the "achievements" array. Never fewer than 4.
- Calibrate the language and scope to the candidate's experience level AT THAT COMPANY:
  * First/oldest job (fresher level): task execution, tool usage, supporting seniors, learning
  * Middle jobs (junior/mid level): independent ownership, feature delivery, cross-team work
  * Most recent job (current level based on {total_exp} total years): leadership, architecture, business impact
- Each bullet must start with a strong action verb.
- Quantify with numbers/percentages where realistic.
- Mirror JD keywords naturally in the bullets.
- Do NOT use generic filler like 'Worked on various tasks'.

Rules:
- Base all tailoring strictly on the provided user details.
- Emphasize skills and experience that match the JD.
- Maintain professional tone.
- Return output in STRICT JSON only.
- Do NOT include explanations, markdown, or extra text.

USER PROFILE:
{json.dumps(user_data, indent=2)}

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object with this exact structure:
{{
  "tailored_resume": {{
    "professional_summary": "Enhanced summary tailored to job",
    "skills_organized": ["skill1", "skill2"],
    "work_experience": [
      {{
        "company": "Company Name",
        "position": "Position",
        "duration": "Duration",
        "achievements": [
          "Strong action-verb bullet 1 with quantified impact",
          "Strong action-verb bullet 2 with quantified impact",
          "Strong action-verb bullet 3 with quantified impact",
          "Strong action-verb bullet 4 with quantified impact",
          "Strong action-verb bullet 5 with quantified impact"
        ]
      }}
    ],
    "education": [
      {{
        "degree": "Degree",
        "institution": "Institution",
        "year": "Year"
      }}
    ],
    "projects": [
      {{
        "name": "Project Name",
        "description": "Enhanced description",
        "technologies": ["tech1", "tech2"]
      }}
    ],
    "certifications": ["cert1", "cert2"]
  }},
  "match_before": 45,
  "match_improvement": 78,
  "changes": [
    {{
      "section": "Professional Summary",
      "type": "modified",
      "original": "Original text",
      "modified": "Modified text",
      "reason": "Why this change improves the resume"
    }}
  ]
}}

IMPORTANT for match scores:
- "match_before": Estimate how well the ORIGINAL resume matches the JD (0-100). Be realistic.
- "match_improvement": Estimate how well the TAILORED resume matches the JD (0-100). Always higher than match_before (typically 10-30 points higher).
"""
        
        response = client.models.generate_content(model=MODEL, contents=prompt)
        result_str = response.text
        
        return parse_tailor_response(result_str)
        
    except Exception as e:
        logger.error("in resume tailoring: %s", e)
        raise
