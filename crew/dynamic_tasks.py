"""
Dynamic Tasks with MongoDB-stored prompts
"""

from crewai import Task, Agent


def create_dynamic_task(task_config: dict, agent: Agent, context_tasks: list = None):
	"""
	Create dynamic task based on configuration
	
	Args:
		task_config: Dict with description, expected_output
		agent: Agent to execute task
		context_tasks: Previous tasks for context
		
	Returns:
		Task: Configured CrewAI task
	"""
	task = Task(
		description=task_config.get("description", "Complete the assigned task"),
		expected_output=task_config.get("expected_output", "Task completion result"),
		agent=agent
	)
	
	if context_tasks:
		task.context = context_tasks
	
	return task
