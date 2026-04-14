"""
Resume Tailor Agent using Gemini AI for intelligent resume customization.
"""

import os
import json
import google.generativeai as genai
from prompt_manager import prompt_manager


def run_resume_tailor(user_profile: dict, job_description: str) -> dict:
    """Execute resume tailoring using Gemini AI."""
    try:
        print(f"Starting resume tailoring with Gemini...")
        
        # Configure Gemini
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
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
        
        prompt = f"""
{tailor_system_prompt}

Your task:
- Tailor a candidate's CV specifically for the provided Job Description (JD).
- Highlight the most relevant skills, experience, and achievements.
- Rewrite content to match keywords and expectations from the JD.
- Do NOT fabricate experience, companies, or skills.
- Preserve truthfulness while optimizing phrasing and structure.
- Use strong, impact-driven bullet points.
- Optimize for ATS (Applicant Tracking Systems).

Rules:
- Base all tailoring strictly on the provided user details.
- Emphasize skills and experience that match the JD.
- De-emphasize unrelated information.
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
        "achievements": ["achievement1", "achievement2"]
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
  "match_improvement": 85,
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
"""
        
        # Call Gemini
        response = model.generate_content(prompt)
        result_str = response.text
        
        # Parse JSON from result
        try:
            # Try to find JSON in the response
            start_idx = result_str.find('{')
            end_idx = result_str.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_str[start_idx:end_idx]
                parsed_result = json.loads(json_str)
                return parsed_result
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw result: {result_str[:500]}")
            # Return fallback structure
            return {
                "tailored_resume": {},
                "match_improvement": 0,
                "changes": [],
                "error": "Failed to parse AI response"
            }
        
    except Exception as e:
        print(f"Error in resume tailoring: {e}")
        raise
