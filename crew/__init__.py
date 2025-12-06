"""
Multi-AI Agent System using CrewAI
Integrates ChatGPT, Gemini, and Claude for enhanced query processing
"""

from .crew_setup import multi_ai_crew, run_multi_ai_query

__all__ = ['multi_ai_crew', 'run_multi_ai_query']
