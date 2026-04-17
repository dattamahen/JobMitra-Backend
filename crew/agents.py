"""
Multi-AI Agents Configuration
All agents use Gemini internally. Names (ChatGPT, Gemini, Claude) are for UI branding only.
"""

import os
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


def _create_gemini_llm():
	"""Shared Gemini LLM instance used by all agents."""
	return ChatGoogleGenerativeAI(
		model="gemini-2.5-flash",
		google_api_key=os.getenv("GEMINI_API_KEY"),
		temperature=0.7
	)


def create_chatgpt_agent():
	"""
	'ChatGPT' branded agent — internally uses Gemini.
	Role: Query Analyzer
	"""
	agent = Agent(
		role="Query Analyzer",
		goal="Analyze user queries and extract key information, intent, and context",
		backstory="""You are an expert query analyzer with deep understanding of natural language.
		You excel at breaking down complex questions, identifying user intent, and extracting
		relevant context. Your analysis forms the foundation for comprehensive responses.""",
		verbose=True,
		allow_delegation=False,
		llm=_create_gemini_llm()
	)
	return agent


def create_gemini_agent():
	"""
	'Gemini' branded agent — uses Gemini.
	Role: Content Enricher
	"""
	agent = Agent(
		role="Content Enricher",
		goal="Enrich and refine the analyzed query with comprehensive information and insights",
		backstory="""You are a knowledge enrichment specialist with vast information across domains.
		You take analyzed queries and expand them with detailed, accurate, and relevant information.
		You excel at providing context, examples, and actionable insights.""",
		verbose=True,
		allow_delegation=False,
		llm=_create_gemini_llm()
	)
	return agent


def create_claude_agent():
	"""
	'Claude' branded agent — internally uses Gemini.
	Role: Response Validator
	"""
	agent = Agent(
		role="Response Validator",
		goal="Validate, refine, and finalize the response ensuring accuracy and completeness",
		backstory="""You are a meticulous validator and quality assurance expert.
		You review enriched content, verify accuracy, ensure completeness, and polish
		the final response. You excel at catching errors, improving clarity, and
		delivering professional, well-structured answers.""",
		verbose=True,
		allow_delegation=False,
		llm=_create_gemini_llm()
	)
	return agent
