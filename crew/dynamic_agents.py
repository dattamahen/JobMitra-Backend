"""
Dynamic Multi-AI Agents with MongoDB-stored prompts
"""

import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()


def create_dynamic_agent(agent_config: dict, llm_provider: str = "openai"):
	"""
	Create dynamic agent based on configuration
	
	Args:
		agent_config: Dict with role, goal, backstory
		llm_provider: "openai", "gemini", or "claude"
		
	Returns:
		Agent: Configured CrewAI agent
	"""
	# Select LLM based on provider
	if llm_provider == "gemini":
		llm = ChatGoogleGenerativeAI(
			model="gemini-1.5-pro",
			google_api_key=os.getenv("GEMINI_API_KEY"),
			temperature=0.7
		)
	elif llm_provider == "claude":
		llm = ChatAnthropic(
			model="claude-3-5-sonnet-20241022",
			anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
			temperature=0.7
		)
	else:  # default to openai
		llm = ChatOpenAI(
			model="gpt-4-turbo-preview",
			api_key=os.getenv("OPENAI_API_KEY"),
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
