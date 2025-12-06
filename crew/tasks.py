"""
Multi-AI Tasks Configuration
Defines sequential tasks for ChatGPT, Gemini, and Claude agents
"""

from crewai import Task, Agent


def create_chatgpt_task(query: str, agent: Agent):
	"""
	Create analysis task for ChatGPT agent
	
	Args:
		query: User's input question
		agent: ChatGPT agent
		
	Returns:
		Task: Analysis task
	"""
	task = Task(
		description=f"""
		Analyze the following user query and extract key information:
		
		Query: "{query}"
		
		Your analysis should include:
		1. Main intent and purpose of the query
		2. Key topics and concepts mentioned
		3. Context and background needed
		4. Specific questions or requests to address
		5. Any ambiguities that need clarification
		
		Provide a structured analysis that will guide the next agent.
		""",
		expected_output="""A structured analysis containing:
		- Query intent and purpose
		- Key topics and concepts
		- Required context
		- Specific questions to answer
		- Clarifications needed""",
		agent=agent
	)
	
	return task


def create_gemini_task(agent: Agent):
	"""
	Create enrichment task for Gemini agent
	
	Args:
		agent: Gemini agent
		
	Returns:
		Task: Enrichment task
	"""
	task = Task(
		description="""
		Based on the previous analysis, enrich and expand the response with:
		
		1. Comprehensive information addressing all identified topics
		2. Relevant examples and use cases
		3. Best practices and recommendations
		4. Additional context and background
		5. Actionable insights and next steps
		
		Ensure the content is:
		- Accurate and up-to-date
		- Well-structured and organized
		- Practical and actionable
		- Easy to understand
		
		Build upon the analysis to create a rich, informative response.
		""",
		expected_output="""An enriched response containing:
		- Comprehensive information on all topics
		- Relevant examples and use cases
		- Best practices and recommendations
		- Actionable insights
		- Well-organized structure""",
		agent=agent
	)
	
	return task


def create_claude_task(agent: Agent):
	"""
	Create validation task for Claude agent
	
	Args:
		agent: Claude agent
		
	Returns:
		Task: Validation task
	"""
	task = Task(
		description="""
		Review and finalize the enriched response by:
		
		1. Validating accuracy of all information
		2. Ensuring completeness - all aspects covered
		3. Improving clarity and readability
		4. Checking for consistency and coherence
		5. Polishing language and structure
		6. Adding final touches and refinements
		
		Deliver a professional, polished final response that:
		- Directly answers the user's query
		- Is accurate and reliable
		- Is well-structured and easy to follow
		- Provides actionable value
		- Maintains professional tone
		
		This is the final output that will be returned to the user.
		""",
		expected_output="""A polished, final response that:
		- Accurately answers the query
		- Is complete and comprehensive
		- Is clear and well-structured
		- Provides actionable insights
		- Maintains professional quality""",
		agent=agent
	)
	
	return task
