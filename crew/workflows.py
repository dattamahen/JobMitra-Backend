"""
Workflow orchestration for interview and CV tailoring
"""

from crewai import Crew
from .dynamic_agents import create_dynamic_agent
from .dynamic_tasks import create_dynamic_task


async def run_interview_workflow(user_profile: dict, prompts: dict) -> dict:
	"""
	Run interview question generation and evaluation workflow
	
	Args:
		user_profile: User profile with name, experience, skills
		prompts: Agent and task prompts from MongoDB
		
	Returns:
		dict: Interview questions and evaluation
	"""
	try:
		# Determine experience level and role type
		experience = user_profile.get('experience', 0)
		skills = user_profile.get('skills', [])
		is_tech = any(s.lower() in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'mongodb', 'aws', 'docker', 'kubernetes'] for s in skills)
		
		# Select appropriate prompt
		if experience <= 1:
			prompt_key = "tech_entry_level_questions" if is_tech else "general_entry_level_questions"
			eval_key = "tech_entry_level_evaluator" if is_tech else "general_entry_level_evaluator"
		elif experience <= 3:
			prompt_key = "tech_junior_questions" if is_tech else "general_junior_questions"
			eval_key = "tech_junior_evaluator" if is_tech else "general_junior_evaluator"
		elif experience <= 7:
			prompt_key = "tech_mid_level_questions" if is_tech else "general_mid_level_questions"
			eval_key = "tech_mid_level_evaluator" if is_tech else "general_mid_level_evaluator"
		else:
			prompt_key = "tech_senior_questions" if is_tech else "general_senior_questions"
			eval_key = "tech_senior_evaluator" if is_tech else "general_senior_evaluator"
		
		# Agent 1: Question Generator
		question_gen_config = {
			"role": "Interview Question Generator",
			"goal": "Generate relevant interview questions based on user profile",
			"backstory": prompts.get("question_prompt", "Expert interviewer")
		}
		question_agent = create_dynamic_agent(question_gen_config, "openai")
		
		# Agent 2: Answer Evaluator
		evaluator_config = {
			"role": "Interview Answer Evaluator",
			"goal": "Evaluate candidate answers and provide detailed feedback",
			"backstory": prompts.get("eval_prompt", "Senior HR professional")
		}
		evaluator_agent = create_dynamic_agent(evaluator_config, "gemini")
		
		# Task 1: Generate Questions
		job_profile = f"Name: {user_profile.get('name', 'Candidate')}, Experience: {user_profile.get('experience', 0)} years, Skills: {', '.join(user_profile.get('skills', []))}"
		question_prompt = prompts.get("question_prompt", "").format(job_profile=job_profile)
		
		question_task_config = {
			"description": question_prompt,
			"expected_output": "Structured interview questions with categories and follow-ups"
		}
		question_task = create_dynamic_task(question_task_config, question_agent)
		
		# Task 2: Evaluate Answers (placeholder - actual answers come from user)
		eval_task_config = {
			"description": """
			Based on the generated questions and candidate profile, provide evaluation criteria:
			
			1. Technical competency assessment framework
			2. Communication skills evaluation points
			3. Soft skills indicators to look for
			4. Scoring rubric (1-10 scale)
			5. Strengths and weaknesses identification method
			
			This will be used to evaluate actual candidate responses.
			""",
			"expected_output": "Evaluation framework and criteria"
		}
		eval_task = create_dynamic_task(eval_task_config, evaluator_agent, [question_task])
		
		# Execute workflow
		crew = Crew(
			agents=[question_agent, evaluator_agent],
			tasks=[question_task, eval_task],
			verbose=True,
			process="sequential"
		)
		
		result = crew.kickoff()
		
		return {
			"success": True,
			"questions": str(result),
			"workflow": "interview_generation"
		}
		
	except Exception as e:
		return {
			"success": False,
			"error": str(e),
			"workflow": "interview_generation"
		}


async def run_cv_tailoring_workflow(user_details: dict, job_description: str, prompts: dict) -> dict:
	"""
	Run CV tailoring and evaluation workflow
	
	Args:
		user_details: User CV/resume details
		job_description: Target job description
		prompts: Agent and task prompts from MongoDB
		
	Returns:
		dict: Tailored CV and evaluation
	"""
	try:
		# Agent 1: CV Tailor
		tailor_config = prompts.get("cv_tailor", {
			"role": "CV Tailoring Specialist",
			"goal": "Tailor CV to match job description and optimize for ATS",
			"backstory": "Expert resume writer who optimizes CVs for specific job roles and ATS systems"
		})
		tailor_agent = create_dynamic_agent(tailor_config, "openai")
		
		# Agent 2: CV Evaluator
		cv_eval_config = prompts.get("cv_evaluator", {
			"role": "CV Quality Evaluator",
			"goal": "Evaluate tailored CV quality and ATS compliance",
			"backstory": "ATS expert and recruiter who validates CV effectiveness"
		})
		cv_eval_agent = create_dynamic_agent(cv_eval_config, "claude")
		
		# Task 1: Tailor CV
		tailor_task_config = {
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
			"expected_output": "Complete tailored CV optimized for the job"
		}
		tailor_task = create_dynamic_task(tailor_task_config, tailor_agent)
		
		# Task 2: Evaluate Tailored CV
		eval_task_config = {
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
			
			Provide detailed evaluation report.
			""",
			"expected_output": "Comprehensive CV evaluation report with scores"
		}
		eval_task = create_dynamic_task(eval_task_config, cv_eval_agent, [tailor_task])
		
		# Execute workflow
		crew = Crew(
			agents=[tailor_agent, cv_eval_agent],
			tasks=[tailor_task, eval_task],
			verbose=True,
			process="sequential"
		)
		
		result = crew.kickoff()
		
		return {
			"success": True,
			"tailored_cv": str(result),
			"workflow": "cv_tailoring"
		}
		
	except Exception as e:
		return {
			"success": False,
			"error": str(e),
			"workflow": "cv_tailoring"
		}


async def evaluate_interview_answers(questions: list, answers: list, user_profile: dict, prompts: dict) -> dict:
	"""
	Evaluate candidate's interview answers
	
	Args:
		questions: List of interview questions
		answers: List of candidate answers
		user_profile: Candidate profile
		prompts: Agent prompts from MongoDB
		
	Returns:
		dict: Evaluation results
	"""
	try:
		# Determine experience level and role type
		experience = user_profile.get('experience', 0)
		skills = user_profile.get('skills', [])
		is_tech = any(s.lower() in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'mongodb', 'aws', 'docker', 'kubernetes'] for s in skills)
		
		# Select appropriate evaluator prompt
		if experience <= 1:
			eval_key = "tech_entry_level_evaluator" if is_tech else "general_entry_level_evaluator"
		elif experience <= 3:
			eval_key = "tech_junior_evaluator" if is_tech else "general_junior_evaluator"
		elif experience <= 7:
			eval_key = "tech_mid_level_evaluator" if is_tech else "general_mid_level_evaluator"
		else:
			eval_key = "tech_senior_evaluator" if is_tech else "general_senior_evaluator"
		
		evaluator_config = {
			"role": "Interview Answer Evaluator",
			"goal": "Evaluate answers comprehensively",
			"backstory": "Expert evaluator assessing technical and soft skills"
		}
		evaluator_agent = create_dynamic_agent(evaluator_config, "gemini")
		
		# Build evaluation prompt
		job_profile = f"Name: {user_profile.get('name')}, Experience: {user_profile.get('experience')} years, Skills: {', '.join(user_profile.get('skills', []))}"
		qa_pairs = chr(10).join([f"Q{i+1}: {q}{chr(10)}A{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers))])
		
		eval_prompt = prompts.get("eval_prompt", "").format(
			candidate_answer=qa_pairs,
			interview_question="Multiple questions answered",
			job_profile=job_profile
		)
		
		eval_task_config = {
			"description": eval_prompt,
			"expected_output": "Comprehensive evaluation with scores, strengths, weaknesses, and feedback"
		}
		eval_task = create_dynamic_task(eval_task_config, evaluator_agent)
		
		crew = Crew(
			agents=[evaluator_agent],
			tasks=[eval_task],
			verbose=True
		)
		
		result = crew.kickoff()
		
		return {
			"success": True,
			"evaluation": str(result),
			"workflow": "answer_evaluation"
		}
		
	except Exception as e:
		return {
			"success": False,
			"error": str(e),
			"workflow": "answer_evaluation"
		}
