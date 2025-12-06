"""
Multi-AI Agents Configuration
Defines ChatGPT, Gemini, and Claude agents for CrewAI
"""

import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()


def create_chatgpt_agent():
	"""
	Create ChatGPT agent using OpenAI GPT-4
	
	Returns:
		Agent: ChatGPT-powered CrewAI agent
	"""
	llm = ChatOpenAI(
		model="gpt-4-turbo-preview",
		api_key=os.getenv("OPENAI_API_KEY"),
		temperature=0.7
	)
	
	agent = Agent(
		role="Query Analyzer",
		goal="Analyze user queries and extract key information, intent, and context",
		backstory="""You are an expert query analyzer with deep understanding of natural language.
		You excel at breaking down complex questions, identifying user intent, and extracting
		relevant context. Your analysis forms the foundation for comprehensive responses.""",
		verbose=True,
		allow_delegation=False,
		llm=llm
	)
	
	return agent


def create_gemini_agent():
	"""
	Create Gemini agent using Google Gemini 1.5 Pro
	
	Returns:
		Agent: Gemini-powered CrewAI agent
	"""
	llm = ChatGoogleGenerativeAI(
		model="gemini-1.5-pro",
		google_api_key=os.getenv("GEMINI_API_KEY"),
		temperature=0.7
	)
	
	agent = Agent(
		role="Content Enricher",
		goal="Enrich and refine the analyzed query with comprehensive information and insights",
		backstory="""You are a knowledge enrichment specialist with vast information across domains.
		You take analyzed queries and expand them with detailed, accurate, and relevant information.
		You excel at providing context, examples, and actionable insights.""",
		verbose=True,
		allow_delegation=False,
		llm=llm
	)
	
	return agent


def create_claude_agent():
	"""
	Create Claude agent using Anthropic Claude 3.5 Sonnet
	
	Returns:
		Agent: Claude-powered CrewAI agent
	"""
	llm = ChatAnthropic(
		model="claude-3-5-sonnet-20241022",
		anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
		temperature=0.7
	)
	
	agent = Agent(
		role="Response Validator",
		goal="Validate, refine, and finalize the response ensuring accuracy and completeness",
		backstory="""You are a meticulous validator and quality assurance expert.
		You review enriched content, verify accuracy, ensure completeness, and polish
		the final response. You excel at catching errors, improving clarity, and
		delivering professional, well-structured answers.""",
		verbose=True,
		allow_delegation=False,
		llm=llm
	)
	
	return agent
