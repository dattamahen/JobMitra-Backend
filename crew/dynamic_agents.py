"""
Dynamic Multi-AI Agents with MongoDB-stored prompts
All providers use Gemini internally. The llm_provider param is for branding only.
"""

import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


def create_dynamic_agent(agent_config: dict, llm_provider: str = "openai"):
	"""
	Create dynamic agent based on configuration.
	All providers route through Gemini internally.

	Args:
		agent_config: Dict with role, goal, backstory
		llm_provider: "openai", "gemini", or "claude" (branding only)

	Returns:
		Agent: Configured CrewAI agent
	"""
	llm = ChatGoogleGenerativeAI(
		model="gemini-2.0-flash",
		google_api_key=os.getenv("GEMINI_API_KEY"),
		temperature=0.7
	)

	agent = Agent(
		role=agent_config.get("role", "AI Assistant"),
		goal=agent_config.get("goal", "Assist with tasks"),
		backstory=agent_config.get("backstory", "You are a helpful AI assistant."),
		verbose=True,
		allow_delegation=False,
		llm=llm
	)

	return agent
