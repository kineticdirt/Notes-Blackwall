#!/usr/bin/env python3
"""
Example: Cross-Chat Communication
Demonstrates how disparate Cursor chat sessions can share findings.
"""

from cross_chat import CrossChatBridge, Finding


def example_publish_and_discover():
    """Example: Publish findings and discover from other sessions."""
    
    print("=== Cross-Chat Communication Example ===\n")
    
    # Simulate Chat Session 1
    print("1. Chat Session 1: Publishing findings...")
    chat1 = CrossChatBridge(session_name="Chat Session 1 - Bug Fixing")
    
    # Publish a bug finding
    finding_id1 = chat1.publish(
        title="Authentication token validation bug",
        content="Found in auth.py line 42. Tokens are not properly validated.",
        category="bug",
        tags=["authentication", "security"],
        related_files=["auth.py"],
        confidence=0.9
    )
    print(f"   Published: {finding_id1}")
    
    # Publish a solution finding
    finding_id2 = chat1.publish(
        title="Solution: Use JWT validation",
        content="Implement proper JWT token validation using PyJWT library.",
        category="solution",
        tags=["authentication", "jwt"],
        related_files=["auth.py"],
        confidence=0.8
    )
    print(f"   Published: {finding_id2}")
    
    # Send heartbeat
    chat1.heartbeat()
    print("   Heartbeat sent\n")
    
    # Simulate Chat Session 2
    print("2. Chat Session 2: Discovering findings...")
    chat2 = CrossChatBridge(session_name="Chat Session 2 - Feature Development")
    
    # Discover bug findings
    bug_findings = chat2.discover(category="bug")
    print(f"   Found {len(bug_findings)} bug finding(s):")
    for finding in bug_findings:
        print(f"     - [{finding.chat_session_id}] {finding.title}")
        print(f"       {finding.content[:60]}...")
    
    # Discover solution findings
    solution_findings = chat2.discover(category="solution")
    print(f"\n   Found {len(solution_findings)} solution finding(s):")
    for finding in solution_findings:
        print(f"     - [{finding.chat_session_id}] {finding.title}")
    
    # Send heartbeat
    chat2.heartbeat()
    print("\n   Heartbeat sent\n")
    
    # Verify listeners
    print("3. Chat Session 1: Verifying listeners...")
    listeners = chat1.verify_listeners()
    print(f"   Active listeners: {listeners['listener_count']}")
    if listeners['listeners']:
        for listener in listeners['listeners']:
            print(f"     - {listener.get('session_name', listener['session_id'])}")
    
    # Search findings
    print("\n4. Chat Session 2: Searching findings...")
    results = chat2.search("authentication")
    print(f"   Found {len(results)} result(s) for 'authentication':")
    for finding in results:
        print(f"     - {finding.title}")
    
    # Show stats
    print("\n5. Session Statistics:")
    stats1 = chat1.get_stats()
    stats2 = chat2.get_stats()
    
    print(f"   Chat 1: {stats1['findings_count']} findings published")
    print(f"   Chat 2: {stats2['findings_count']} findings published")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    example_publish_and_discover()
