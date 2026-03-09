"""
Autonomous CLI for Blackwall.
Agents operate autonomously to achieve goals.
"""

import click
from pathlib import Path
from blackwall.autonomous.orchestrator import AutonomousOrchestrator
from blackwall.autonomous.autonomous_protection_agent import AutonomousProtectionAgent
from blackwall.autonomous.self_coordinator import SelfCoordinator


@click.group()
def cli():
    """Blackwall: Autonomous AI Protection System"""
    pass


@cli.command()
@click.argument('goal')
@click.option('--priority', default=5, type=int, help='Goal priority (1-10)')
def achieve(goal, priority):
    """Autonomously achieve a goal"""
    orchestrator = AutonomousOrchestrator()
    
    click.echo(f"🎯 Setting autonomous goal: {goal}")
    
    result = orchestrator.achieve_goal(goal, priority=priority)
    
    click.echo(f"✓ Goal set (ID: {result['goal_id']})")
    click.echo("🤖 Agents are working autonomously to achieve this goal...")
    
    status = orchestrator.get_autonomous_status()
    click.echo(f"\nStatus:")
    click.echo(f"  Active goals: {status['active_goals']}")
    click.echo(f"  Pending goals: {status['pending_goals']}")


@cli.command()
@click.argument('content_path')
def protect(content_path):
    """Autonomously protect content"""
    agent = AutonomousProtectionAgent()
    
    click.echo(f"🛡️  Autonomous protection: {content_path}")
    
    result = agent.autonomous_protect(content_path)
    
    if result.get('success'):
        click.echo(f"✓ Protected: {result['output_path']}")
        click.echo(f"✓ UUID: {result['uuid']}")
    else:
        click.echo(f"✗ Protection failed: {result.get('error')}")


@cli.command()
@click.argument('directory')
def batch_protect(directory):
    """Autonomously protect all content in directory"""
    agent = AutonomousProtectionAgent()
    
    click.echo(f"🛡️  Autonomous batch protection: {directory}")
    
    results = agent.autonomous_batch_protect(directory)
    
    click.echo(f"\n✓ Batch protection complete:")
    click.echo(f"  Protected: {len(results['protected'])}")
    click.echo(f"  Failed: {len(results['failed'])}")
    click.echo(f"  Total: {results['total']}")


@cli.command()
def status():
    """Get autonomous system status"""
    orchestrator = AutonomousOrchestrator()
    coordinator = SelfCoordinator()
    
    click.echo("🤖 Blackwall Autonomous System Status\n")
    
    # Orchestrator status
    orch_status = orchestrator.get_autonomous_status()
    click.echo("Orchestrator:")
    click.echo(f"  Active goals: {orch_status['active_goals']}")
    click.echo(f"  Pending goals: {orch_status['pending_goals']}")
    click.echo(f"  Completed goals: {orch_status['completed_goals']}")
    
    # Coordinator status
    coord_status = coordinator.get_coordination_status()
    click.echo(f"\nSelf-Coordinator:")
    click.echo(f"  Registered agents: {coord_status['registered_agents']}")
    click.echo(f"  Active coordinations: {coord_status['active_coordinations']}")
    
    if coord_status['agents']:
        click.echo(f"\nAgents:")
        for agent in coord_status['agents']:
            click.echo(f"  - {agent['agent_id']} ({agent['agent_type']})")


@cli.command()
@click.argument('task')
def coordinate(task):
    """Autonomously coordinate agents for a task"""
    coordinator = SelfCoordinator()
    
    click.echo(f"🤝 Autonomous coordination: {task}")
    
    result = coordinator.autonomous_coordinate(task)
    
    click.echo(f"✓ Coordination created (ID: {result['coordination_id']})")
    click.echo(f"✓ Agents involved: {len(result['agents'])}")
    
    for agent in result['agents']:
        click.echo(f"  - {agent['agent_id']} ({agent['agent_type']})")


if __name__ == '__main__':
    cli()
