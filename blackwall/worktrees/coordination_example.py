#!/usr/bin/env python3
"""
Example: Agent Coordination with Timeout and Hanging Detection
Demonstrates handling race conditions, timeouts, and hanging processes.
"""

import time
from coordination_integration import CoordinatedCrossChatBridge, create_coordinated_bridge


def example_coordination():
    """Example: Coordinating multiple agents with timeout handling."""
    
    print("=== Agent Coordination Example ===\n")
    
    # Simulate Agent 1
    print("1. Agent 1: Starting operation...")
    agent1 = create_coordinated_bridge(session_name="Agent 1 - Code Analysis")
    
    # Start operation with time estimate
    operation_id = agent1.start_operation(
        operation_description="Analyze codebase for bugs",
        expected_duration_seconds=120.0  # 2 minutes
    )
    print(f"   Operation ID: {operation_id}")
    
    # Provide time estimate
    agent1.coordinator.provide_time_estimate(
        operation_id=operation_id,
        agent_id=agent1.session_id,
        estimated_seconds=120.0,
        confidence=0.8
    )
    print("   Time estimate: 120 seconds (confidence: 0.8)")
    
    # Send heartbeat
    agent1.send_heartbeat()
    print("   Heartbeat sent\n")
    
    # Simulate Agent 2 waiting for Agent 1
    print("2. Agent 2: Waiting for Agent 1...")
    agent2 = create_coordinated_bridge(session_name="Agent 2 - Testing")
    
    # Request time estimate
    estimate = agent2.request_time_estimate(operation_id)
    if estimate:
        print(f"   Received estimate: {estimate.estimated_seconds} seconds")
        print(f"   Will wait up to: {estimate.estimated_seconds * 1.5:.0f} seconds")
    
    # Wait for Agent 1 (with timeout)
    print("   Waiting for Agent 1 to complete...")
    success = agent2.wait_for_other_session(
        session_id=agent1.session_id,
        timeout_seconds=180.0  # 3 minutes max
    )
    
    if success:
        print("   ✓ Agent 1 completed!")
    else:
        print("   ✗ Timeout - Agent 1 may be hanging")
    
    # Check for hanging agents
    print("\n3. Checking for hanging agents...")
    hanging = agent2.check_hanging_sessions()
    if hanging:
        print(f"   Found {len(hanging)} hanging agent(s):")
        for agent in hanging:
            print(f"     - {agent['agent_id']}: {agent['status']}")
    else:
        print("   No hanging agents detected")
    
    # Get coordination status
    print("\n4. Agent 1 Status:")
    status1 = agent1.get_coordination_status()
    print(f"   Status: {status1['status']}")
    print(f"   Active actions: {status1['active_action_count']}")
    print(f"   Last heartbeat: {status1['last_heartbeat']}")
    
    print("\n5. Agent 2 Status:")
    status2 = agent2.get_coordination_status()
    print(f"   Status: {status2['status']}")
    print(f"   Cross-chat listeners: {status2['cross_chat_listeners']}")
    
    # Complete operation
    print("\n6. Agent 1: Completing operation...")
    agent1.complete_operation(operation_id, success=True)
    print("   ✓ Operation completed")
    
    # Final status
    print("\n7. Final Status Check:")
    final_status = agent1.get_coordination_status()
    print(f"   Status: {final_status['status']}")
    print(f"   Active actions: {final_status['active_action_count']}")
    
    print("\n=== Example Complete ===")


def example_hanging_detection():
    """Example: Detecting hanging processes."""
    
    print("\n=== Hanging Process Detection Example ===\n")
    
    agent = create_coordinated_bridge(session_name="Test Agent")
    
    # Start operation
    print("1. Starting long operation...")
    op_id = agent.start_operation(
        operation_description="Simulated hanging operation",
        expected_duration_seconds=10.0  # Should complete in 10 seconds
    )
    
    # Simulate hanging (don't complete operation)
    print("2. Simulating hang (not completing operation)...")
    print("   Waiting 15 seconds...")
    time.sleep(15)
    
    # Check health
    print("3. Checking agent health...")
    health = agent.coordinator.health_monitor.check_health(agent.session_id)
    print(f"   Status: {health['status']}")
    print(f"   Is hanging: {health['is_hanging']}")
    print(f"   Elapsed: {health.get('elapsed_since_heartbeat', 0):.1f} seconds")
    
    # Check for hanging agents
    hanging = agent.check_hanging_sessions()
    if hanging:
        print(f"\n4. Detected {len(hanging)} hanging agent(s):")
        for h in hanging:
            print(f"   - {h['agent_id']}: {h['status']}")
    
    print("\n=== Hanging Detection Example Complete ===")


if __name__ == "__main__":
    example_coordination()
    example_hanging_detection()
