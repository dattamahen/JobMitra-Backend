"""
CrewAI agent setup and execution module.
Defines agents, tasks, and crew for query processing and resume enhancement.
"""

import logging
logger = logging.getLogger(__name__)

import os
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from prompt_manager import prompt_manager


def setup_llm():
    """
    Setup Gemini LLM. All agents route through Gemini internally.
    
    Returns:
        ChatGoogleGenerativeAI: Configured Gemini language model
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=gemini_api_key,
        temperature=0.7
    )
    
    return llm


def create_researcher_agent():
    """
    Create a researcher agent specialized in analyzing and answering queries.
    
    Returns:
        Agent: Configured CrewAI researcher agent
    """
    # Setup the language model
    llm = setup_llm()
    
    # Create researcher agent with specific role and capabilities
    variant = prompt_manager.get_random("query_analysis")
    
    researcher = Agent(
        role="Researcher",
        goal="Analyze and answer user queries with accurate, comprehensive, and helpful information",
        backstory=variant.get("system_prompt"),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return researcher


def create_resume_matcher_agent():
    """
    Create a resume matcher agent specialized in comparing resumes with job descriptions.
    
    Returns:
        Agent: Configured CrewAI resume matcher agent
    """
    # Setup the language model
    llm = setup_llm()
    
    # Create resume matcher agent
    variant = prompt_manager.get_random("resume_validation")
    
    resume_matcher = Agent(
        role="Resume Validator",
        goal="Compare resume with job description and return match percentage and gaps",
        backstory=variant.get("system_prompt"),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return resume_matcher


def create_resume_improver_agent():
    """
    Create a resume improver agent specialized in providing enhancement suggestions.
    
    Returns:
        Agent: Configured CrewAI resume improver agent
    """
    # Setup the language model
    llm = setup_llm()
    
    # Create resume improver agent
    variant = prompt_manager.get_random("resume_enhancement")
    
    resume_improver = Agent(
        role="Enhancement Advisor",
        goal="Suggest updates to the resume based on validation analysis and best practices",
        backstory=variant.get("system_prompt"),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return resume_improver


def create_resume_finalizer_agent():
    """
    Create a resume finalizer agent specialized in generating improved resume versions.
    
    Returns:
        Agent: Configured CrewAI resume finalizer agent
    """
    # Setup the language model
    llm = setup_llm()
    
    # Create resume finalizer agent
    variant = prompt_manager.get_random("resume_enhancement")
    
    resume_finalizer = Agent(
        role="Resume Generator",
        goal="Use improvement suggestions to generate the enhanced final version of the resume",
        backstory=variant.get("system_prompt"),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    return resume_finalizer


def create_research_task(query: str, agent: Agent):
    """
    Create a research task for the given query and agent.
    
    Args:
        query (str): User's input query to be analyzed
        agent (Agent): The agent that will execute this task
        
    Returns:
        Task: Configured CrewAI task
    """
    # Create task with specific description and expected output
    research_task = Task(
        description=f"""
        Analyze and provide a comprehensive answer to the following query: "{query}"
        
        Your response should:
        1. Directly address the user's question or request
        2. Provide accurate and up-to-date information
        3. Be well-structured and easy to understand
        4. Include relevant examples or actionable advice when appropriate
        5. Be concise yet thorough
        
        If the query is unclear or needs clarification, acknowledge this and provide 
        the best possible interpretation along with your response.
        """,
        expected_output="""A clear, comprehensive, and helpful response that directly 
        addresses the user's query with accurate information and actionable insights.""",
        agent=agent
    )
    
    return research_task


def create_resume_matching_task(resume: str, job_description: str, agent: Agent):
    """
    Create a resume matching task to analyze compatibility between resume and job description.
    
    Args:
        resume (str): The candidate's resume content
        job_description (str): The job description to match against
        agent (Agent): The resume matcher agent that will execute this task
        
    Returns:
        Task: Configured CrewAI resume matching task
    """
    matching_task = Task(
        description=f"""
        Analyze the compatibility between the provided resume and job description.
        
        RESUME:
        {resume}
        
        JOB DESCRIPTION:
        {job_description}
        
        Your analysis should include:
        1. Overall match percentage (0-100%)
        2. Skills analysis:
           - Required skills present in resume
           - Required skills missing from resume
           - Additional relevant skills in resume
        3. Experience analysis:
           - Years of experience match
           - Industry experience relevance
           - Role level compatibility
        4. Education and certification analysis
        5. Key gaps that need to be addressed
        6. ATS optimization assessment
        7. Specific recommendations for improvement areas
        
        Provide a detailed, structured analysis that will be used by the next agent 
        to suggest specific improvements.
        """,
        expected_output="""A comprehensive analysis report including:
        - Match percentage with justification
        - Detailed skills gap analysis
        - Experience and qualification assessment
        - Specific areas needing improvement
        - ATS compatibility score and recommendations""",
        agent=agent
    )
    
    return matching_task


def create_resume_improvement_task(agent: Agent):
    """
    Create a resume improvement task that builds on the matching analysis.
    
    Args:
        agent (Agent): The resume improver agent that will execute this task
        
    Returns:
        Task: Configured CrewAI resume improvement task
    """
    improvement_task = Task(
        description="""
        Based on the previous resume matching analysis, provide specific, actionable 
        improvement suggestions for the resume.
        
        Your suggestions should include:
        1. Content improvements:
           - Skills to add or emphasize
           - Experience descriptions to enhance
           - Keywords to incorporate for ATS optimization
           - Quantifiable achievements to highlight
        2. Structure improvements:
           - Section reorganization recommendations
           - Format optimization for ATS parsing
           - Length and readability enhancements
        3. Industry-specific customizations:
           - Role-specific terminology to include
           - Industry buzzwords and trends
           - Certification or skill priorities
        4. Gap-filling strategies:
           - How to address missing requirements
           - Ways to reframe existing experience
           - Suggestions for skill development
        
        Provide concrete, implementable suggestions that the next agent can use 
        to generate an improved resume version.
        """,
        expected_output="""Detailed improvement recommendations including:
        - Specific content additions and modifications
        - Structural and formatting suggestions
        - ATS optimization strategies
        - Industry-specific customizations
        - Implementation priority ranking""",
        agent=agent
    )
    
    return improvement_task


def create_resume_generation_task(original_resume: str, agent: Agent):
    """
    Create a resume generation task that produces the final improved resume.
    
    Args:
        original_resume (str): The original resume content
        agent (Agent): The resume finalizer agent that will execute this task
        
    Returns:
        Task: Configured CrewAI resume generation task
    """
    generation_task = Task(
        description=f"""
        Using the original resume and the improvement suggestions from the previous analysis, 
        generate an enhanced version of the resume.
        
        ORIGINAL RESUME:
        {original_resume}
        
        Requirements for the improved resume:
        1. Implement all feasible improvement suggestions
        2. Maintain professional formatting and structure
        3. Ensure ATS compatibility with proper keyword density
        4. Preserve original qualifications while enhancing presentation
        5. Add relevant keywords and industry terminology
        6. Quantify achievements where possible
        7. Improve action verbs and impact statements
        8. Ensure logical flow and readability
        
        Generate a complete, polished resume that addresses the identified gaps 
        and incorporates the suggested improvements while maintaining authenticity.
        """,
        expected_output="""A complete, improved resume that:
        - Addresses the skill gaps identified in the analysis
        - Incorporates ATS optimization improvements
        - Features enhanced content and formatting
        - Maintains professional standards and authenticity
        - Is ready for job application submission""",
        agent=agent
    )
    
    return generation_task


def run_crew_ai(query: str) -> str:
    """
    Execute CrewAI workflow to process and answer the user query.
    
    Args:
        query (str): User's input query
        
    Returns:
        str: AI-generated response from the researcher agent
    """
    try:
        logger.debug("Processing query with CrewAI: %s", query)
        
        # Create the researcher agent
        researcher_agent = create_researcher_agent()
        
        # Create the research task
        research_task = create_research_task(query, researcher_agent)
        
        # Create and configure the crew
        crew = Crew(
            agents=[researcher_agent],
            tasks=[research_task],
            verbose=True
        )
        
        # Execute the crew workflow
        result = crew.kickoff()
        
        # Extract the response from the result
        response = str(result)
        
        logger.debug("CrewAI processing completed successfully")
        return response
        
    except Exception as e:
        logger.error("in CrewAI processing: %s", e)
        # Return a fallback response in case of errors
        return f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try again or rephrase your question."


def run_resume_enhancement_crew(resume: str, job_description: str) -> str:
    """
    Execute CrewAI workflow for resume enhancement with 3-agent chain.
    
    Args:
        resume (str): The candidate's resume content
        job_description (str): The job description to match against
        
    Returns:
        str: Enhanced resume generated by the 3-agent chain
    """
    try:
        logger.debug("Starting resume enhancement with CrewAI...")
        logger.debug("Resume length: %s characters", len(resume))
        logger.debug("Job description length: %s characters", len(job_description))
        
        # Create the three agents
        logger.info("Creating resume enhancement agents...")
        resume_matcher = create_resume_matcher_agent()
        resume_improver = create_resume_improver_agent()
        resume_finalizer = create_resume_finalizer_agent()
        
        # Create the three tasks in sequence
        logger.info("Creating sequential tasks...")
        matching_task = create_resume_matching_task(resume, job_description, resume_matcher)
        improvement_task = create_resume_improvement_task(resume_improver)
        generation_task = create_resume_generation_task(resume, resume_finalizer)
        
        # Set up task dependencies (each task uses output from previous)
        improvement_task.context = [matching_task]
        generation_task.context = [matching_task, improvement_task]
        
        # Create and configure the crew with all agents and tasks
        logger.info("Configuring crew with sequential execution...")
        crew = Crew(
            agents=[resume_matcher, resume_improver, resume_finalizer],
            tasks=[matching_task, improvement_task, generation_task],
            verbose=True,
            process="sequential"  # Ensure tasks run in order
        )
        
        # Execute the crew workflow
        logger.info("Executing resume enhancement workflow...")
        result = crew.kickoff()
        
        # Extract the final enhanced resume
        enhanced_resume = str(result)
        
        logger.debug("Resume enhancement completed successfully")
        logger.debug("Enhanced resume length: %s characters", len(enhanced_resume))
        return enhanced_resume
        
    except Exception as e:
        logger.error("in resume enhancement processing: %s", e)
        # Return a fallback response in case of errors
        return f"I apologize, but I encountered an error while enhancing your resume: {str(e)}. Please try again with a different resume or job description."


# Example usage functions for testing
async def test_crew_ai():
    """Test function to verify CrewAI setup is working correctly."""
    test_query = "What are the benefits of using Python for web development?"
    response = run_crew_ai(test_query)
    logger.debug("Test Query: %s", test_query)
    logger.debug("Response: %s", response)
    return response


async def test_resume_enhancement():
    """Test function to verify resume enhancement workflow."""
    test_resume = """
    John Doe
    Software Developer
    Email: john.doe@email.com
    Phone: (555) 123-4567
    
    EXPERIENCE:
    Software Developer at TechCorp (2020-2023)
    - Developed web applications
    - Worked with Python and JavaScript
    - Collaborated with team members
    
    EDUCATION:
    Bachelor's in Computer Science, University XYZ (2016-2020)
    
    SKILLS:
    Python, JavaScript, HTML, CSS
    """
    
    test_job_description = """
    Senior Full Stack Developer
    
    We are looking for an experienced Full Stack Developer to join our team.
    
    Requirements:
    - 5+ years of experience in web development
    - Strong proficiency in Python, JavaScript, React, Node.js
    - Experience with databases (SQL, MongoDB)
    - Knowledge of cloud platforms (AWS, Azure)
    - Experience with DevOps practices
    - Strong problem-solving skills
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Implement best practices for code quality
    - Mentor junior developers
    """
    
    enhanced_resume = run_resume_enhancement_crew(test_resume, test_job_description)
    logger.debug("Original Resume Length: %s", len(test_resume))
    logger.debug("Enhanced Resume Length: %s", len(enhanced_resume))
    logger.debug("Enhanced Resume Preview: %s...", enhanced_resume[:500])
    return enhanced_resume
