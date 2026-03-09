"""
Example usage of the Claude sub-agent system.
"""

from coordinator import AgentCoordinator
from agents.code_agent import CodeAgent
from agents.research_agent import ResearchAgent
from agents.review_agent import ReviewAgent


def example_multi_agent_coordination():
    """Example of multiple agents working together."""
    
    # Initialize coordinator
    coordinator = AgentCoordinator()
    
    # Create specialized agents
    code_agent = CodeAgent()
    research_agent = ResearchAgent()
    review_agent = ReviewAgent()
    
    # Register agents
    coordinator.register_agent(code_agent)
    coordinator.register_agent(research_agent)
    coordinator.register_agent(review_agent)
    
    # Example workflow: Research -> Code -> Review
    
    # Step 1: Research agent researches a topic
    research_agent.research_topic("Best practices for image watermarking")
    research_agent.log("Found relevant papers and documentation")
    research_agent.complete_intent()
    
    # Step 2: Code agent implements based on research
    code_agent.implement_feature(
        "Add robust watermarking to image processor",
        files=["core/image_processor.py", "core/watermarking.py"]
    )
    code_agent.log("Implementation in progress...")
    code_agent.complete_intent()
    
    # Step 3: Review agent reviews the code
    review_agent.review_code(
        "Review watermarking implementation",
        files=["core/watermarking.py"]
    )
    review_agent.log("Code review complete - looks good!")
    review_agent.complete_intent()
    
    # Get coordination summary
    summary = coordinator.get_coordination_summary()
    print("Coordination Summary:")
    print(f"  Agents: {summary['agents']['total_agents']}")
    print(f"  Pending tasks: {summary['pending_tasks']}")
    print(f"  Active tasks: {summary['active_tasks']}")
    print(f"  Completed tasks: {summary['completed_tasks']}")
    
    # Get recent messages
    messages = coordinator.ledger.get_messages()
    print("\nRecent Messages:")
    for msg in messages[-5:]:
        print(f"  [{msg['agent_id']}] {msg['message']}")


def example_task_assignment():
    """Example of task assignment."""
    
    coordinator = AgentCoordinator()
    
    code_agent = CodeAgent()
    coordinator.register_agent(code_agent)
    
    # Assign tasks
    task1 = coordinator.assign_task(
        "Implement user authentication",
        agent_type="code",
        priority=8
    )
    
    task2 = coordinator.assign_task(
        "Add error handling",
        agent_type="code",
        priority=5
    )
    
    # Distribute tasks
    coordinator.distribute_tasks()
    
    print(f"Task 1 ID: {task1}")
    print(f"Task 2 ID: {task2}")


if __name__ == "__main__":
    print("=== Multi-Agent Coordination Example ===")
    example_multi_agent_coordination()
    
    print("\n=== Task Assignment Example ===")
    example_task_assignment()
