"""
Workflow orchestration for interview and CV tailoring.
Uses file-based prompt_manager for agent backstories.
"""

from crewai import Crew
from .dynamic_agents import create_dynamic_agent
from .dynamic_tasks import create_dynamic_task
from prompt_manager import prompt_manager


async def run_interview_workflow(user_profile: dict, prompts: dict) -> dict:
	"""
	Run interview question generation and evaluation workflow.

	Args:
		user_profile: User profile with name, experience, skills
		prompts: Prompt system_prompt strings (question_prompt, eval_prompt)

	Returns:
		dict: Interview questions and evaluation
	"""
	try:
		question_agent = create_dynamic_agent({
			"role": "Interview Question Generator",
			"goal": "Generate relevant interview questions based on user profile",
			"backstory": prompts.get("question_prompt", prompt_manager.get_random("interview_questions").get("system_prompt")),
		}, "openai")

		evaluator_agent = create_dynamic_agent({
			"role": "Interview Answer Evaluator",
			"goal": "Evaluate candidate answers and provide detailed feedback",
			"backstory": prompts.get("eval_prompt", prompt_manager.get_random("interview_evaluation").get("system_prompt")),
		}, "gemini")

		job_profile = (
			f"Name: {user_profile.get('name', 'Candidate')}, "
			f"Experience: {user_profile.get('experience', 0)} years, "
			f"Skills: {', '.join(user_profile.get('skills', []))}"
		)

		question_task = create_dynamic_task({
			"description": f"{prompts.get('question_prompt', '')}\n\nCandidate Profile: {job_profile}",
			"expected_output": "Structured interview questions with categories and follow-ups",
		}, question_agent)

		eval_task = create_dynamic_task({
			"description": """
			Based on the generated questions and candidate profile, provide evaluation criteria:
			1. Technical competency assessment framework
			2. Communication skills evaluation points
			3. Soft skills indicators to look for
			4. Scoring rubric (1-10 scale)
			5. Strengths and weaknesses identification method
			""",
			"expected_output": "Evaluation framework and criteria",
		}, evaluator_agent, [question_task])

		crew = Crew(
			agents=[question_agent, evaluator_agent],
			tasks=[question_task, eval_task],
			verbose=True,
			process="sequential",
		)

		result = crew.kickoff()

		return {
			"success": True,
			"questions": str(result),
			"workflow": "interview_generation",
		}

	except Exception as e:
		return {"success": False, "error": str(e), "workflow": "interview_generation"}


async def run_cv_tailoring_workflow(user_details: dict, job_description: str, prompts: dict) -> dict:
	"""
	Run CV tailoring and evaluation workflow.

	Args:
		user_details: User CV/resume details
		job_description: Target job description
		prompts: Prompt system_prompt strings (cv_tailor, cv_evaluator)

	Returns:
		dict: Tailored CV and evaluation
	"""
	try:
		tailor_agent = create_dynamic_agent({
			"role": "CV Tailoring Specialist",
			"goal": "Tailor CV to match job description and optimize for ATS",
			"backstory": prompts.get("cv_tailor", prompt_manager.get_random("resume_tailoring").get("system_prompt")),
		}, "openai")

		cv_eval_agent = create_dynamic_agent({
			"role": "CV Quality Evaluator",
			"goal": "Evaluate tailored CV quality and ATS compliance",
			"backstory": prompts.get("cv_evaluator", prompt_manager.get_random("resume_validation").get("system_prompt")),
		}, "claude")

		tailor_task = create_dynamic_task({
			"description": f"""
			Tailor the following CV for the job description:

			USER DETAILS:
			{user_details}

			JOB DESCRIPTION:
			{job_description}

			Requirements:
			1. Match keywords from job description
			2. Optimize for ATS scanning
			3. Highlight relevant experience
			4. Quantify achievements
			5. Maintain professional format
			6. Add missing relevant skills
			7. Reorder sections for impact

			Provide complete tailored CV.
			""",
			"expected_output": "Complete tailored CV optimized for the job",
		}, tailor_agent)

		eval_task = create_dynamic_task({
			"description": """
			Evaluate the tailored CV:
			1. ATS compatibility score (0-100)
			2. Keyword match percentage
			3. Format and structure quality
			4. Content relevance score
			5. Improvement suggestions
			6. Strengths identified
			7. Weaknesses to address
			8. Overall recommendation
			""",
			"expected_output": "Comprehensive CV evaluation report with scores",
		}, cv_eval_agent, [tailor_task])

		crew = Crew(
			agents=[tailor_agent, cv_eval_agent],
			tasks=[tailor_task, eval_task],
			verbose=True,
			process="sequential",
		)

		result = crew.kickoff()

		return {
			"success": True,
			"tailored_cv": str(result),
			"workflow": "cv_tailoring",
		}

	except Exception as e:
		return {"success": False, "error": str(e), "workflow": "cv_tailoring"}


async def evaluate_interview_answers(questions: list, answers: list, user_profile: dict, prompts: dict) -> dict:
	"""
	Evaluate candidate's interview answers.

	Args:
		questions: List of interview questions
		answers: List of candidate answers
		user_profile: Candidate profile
		prompts: Prompt system_prompt strings

	Returns:
		dict: Evaluation results
	"""
	try:
		eval_backstory = prompts.get(
			"eval_prompt",
			prompt_manager.get_random("interview_evaluation").get("system_prompt"),
		)

		evaluator_agent = create_dynamic_agent({
			"role": "Interview Answer Evaluator",
			"goal": "Evaluate answers comprehensively",
			"backstory": eval_backstory,
		}, "gemini")

		job_profile = (
			f"Name: {user_profile.get('name')}, "
			f"Experience: {user_profile.get('experience')} years, "
			f"Skills: {', '.join(user_profile.get('skills', []))}"
		)
		qa_pairs = "\n".join(
			[f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))]
		)

		eval_task = create_dynamic_task({
			"description": f"""
			Evaluate the following interview answers for this candidate:

			Candidate: {job_profile}

			{qa_pairs}

			Provide comprehensive evaluation with scores, strengths, weaknesses, and feedback.
			""",
			"expected_output": "Comprehensive evaluation with scores, strengths, weaknesses, and feedback",
		}, evaluator_agent)

		crew = Crew(
			agents=[evaluator_agent],
			tasks=[eval_task],
			verbose=True,
		)

		result = crew.kickoff()

		return {
			"success": True,
			"evaluation": str(result),
			"workflow": "answer_evaluation",
		}

	except Exception as e:
		return {"success": False, "error": str(e), "workflow": "answer_evaluation"}
