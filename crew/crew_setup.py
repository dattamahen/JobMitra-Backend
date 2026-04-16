"""
Multi-AI Crew Orchestrator
Coordinates ChatGPT, Gemini, and Claude agents in sequential workflow
"""

import logging
logger = logging.getLogger(__name__)

from crewai import Crew
from .agents import create_chatgpt_agent, create_gemini_agent, create_claude_agent
from .tasks import create_chatgpt_task, create_gemini_task, create_claude_task


def create_multi_ai_crew(query: str):
	"""
	Create and configure multi-AI crew with sequential execution
	
	Args:
		query: User's input question
		
	Returns:
		Crew: Configured CrewAI crew
	"""
	# Create agents
	chatgpt_agent = create_chatgpt_agent()
	gemini_agent = create_gemini_agent()
	claude_agent = create_claude_agent()
	
	# Create tasks
	task_chatgpt = create_chatgpt_task(query, chatgpt_agent)
	task_gemini = create_gemini_task(gemini_agent)
	task_claude = create_claude_task(claude_agent)
	
	# Set task dependencies
	task_gemini.context = [task_chatgpt]
	task_claude.context = [task_chatgpt, task_gemini]
	
	# Create crew with sequential execution
	crew = Crew(
		agents=[chatgpt_agent, gemini_agent, claude_agent],
		tasks=[task_chatgpt, task_gemini, task_claude],
		verbose=True,
		process="sequential"
	)
	
	return crew


def run_multi_ai_query(query: str) -> dict:
	"""
	Execute multi-AI crew workflow with fallback handling
	
	Args:
		query: User's input question
		
	Returns:
		dict: Response with result and metadata
	"""
	try:
		logger.debug("[Multi-AI] Processing query: %s...", query[:100])
		
		# Create and execute crew
		crew = create_multi_ai_crew(query)
		result = crew.kickoff()
		
		response = {
			"success": True,
			"response": str(result),
			"providers_used": ["ChatGPT", "Gemini", "Claude"],
			"workflow": "sequential"
		}
		
		logger.info("[Multi-AI] Query processed successfully")
		return response
		
	except Exception as e:
		logger.debug("[Multi-AI] Error: %s", e)
		
		# Fallback to single provider
		try:
			from crew_agent import run_crew_ai
			fallback_result = run_crew_ai(query)
			
			return {
				"success": True,
				"response": fallback_result,
				"providers_used": ["ChatGPT (fallback)"],
				"workflow": "fallback",
				"note": f"Multi-AI failed, used fallback: {str(e)}"
			}
		except Exception as fallback_error:
			return {
				"success": False,
				"response": f"Unable to process query. Error: {str(e)}",
				"providers_used": [],
				"workflow": "failed",
				"error": str(fallback_error)
			}


# Pre-configured crew instance (optional)
multi_ai_crew = None
