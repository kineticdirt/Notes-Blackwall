#!/usr/bin/env python3
"""
CLI for cross-chat communication.
Enables Cursor chat sessions to share findings and verify others are listening.
"""

import argparse
import json
from pathlib import Path
from .cross_chat import CrossChatBridge, Finding


def publish_finding(args):
    """Publish a finding."""
    bridge = CrossChatBridge(session_name=args.session_name)
    
    # Read content from file if provided
    content = args.content
    if args.file:
        content = Path(args.file).read_text()
    
    finding_id = bridge.publish(
        title=args.title,
        content=content,
        category=args.category,
        tags=args.tags.split(",") if args.tags else [],
        related_files=args.files.split(",") if args.files else [],
        confidence=args.confidence
    )
    
    print(f"Published finding: {finding_id}")
    print(f"Title: {args.title}")
    print(f"Category: {args.category}")
    
    # Send heartbeat
    bridge.heartbeat()
    print("Heartbeat sent")


def discover_findings(args):
    """Discover findings from other chats."""
    bridge = CrossChatBridge(session_name=args.session_name)
    
    findings = bridge.discover(
        category=args.category,
        tags=args.tags.split(",") if args.tags else [],
        limit=args.limit
    )
    
    if not findings:
        print("No findings found.")
        return
    
    print(f"\nFound {len(findings)} finding(s):\n")
    for finding in findings:
        print(f"  [{finding.category}] {finding.title}")
        print(f"  From: {finding.chat_session_id}")
        print(f"  Content: {finding.content[:100]}...")
        if finding.tags:
            print(f"  Tags: {', '.join(finding.tags)}")
        print()


def search_findings(args):
    """Search findings."""
    bridge = CrossChatBridge(session_name=args.session_name)
    
    findings = bridge.search(args.query, limit=args.limit)
    
    if not findings:
        print("No findings found.")
        return
    
    print(f"\nFound {len(findings)} finding(s) for '{args.query}':\n")
    for finding in findings:
        print(f"  [{finding.category}] {finding.title}")
        print(f"  From: {finding.chat_session_id}")
        print(f"  {finding.content[:150]}...")
        print()


def verify_listeners(args):
    """Verify other sessions are listening."""
    bridge = CrossChatBridge(session_name=args.session_name)
    
    # Send heartbeat first
    bridge.heartbeat()
    
    # Check listeners
    result = bridge.verify_listeners()
    
    print(f"Active listeners: {result['listener_count']}")
    if result['listeners']:
        print("\nActive sessions:")
        for listener in result['listeners']:
            print(f"  - {listener.get('session_name', listener['session_id'])}")
            print(f"    Findings: {listener['findings_count']}")
            print(f"    Last seen: {listener['last_seen']}")
    else:
        print("\nNo other active sessions detected.")
        print("(Other chats need to send heartbeats to be visible)")


def show_stats(args):
    """Show session statistics."""
    bridge = CrossChatBridge(session_name=args.session_name)
    
    stats = bridge.get_stats()
    
    if not stats:
        print("Session not found.")
        return
    
    print(f"\nSession: {stats.get('session_name', stats['session_id'])}")
    print(f"Findings published: {stats['findings_count']}")
    print(f"Last seen: {stats['last_seen']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-Chat Communication CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--session-name",
        help="Session name (for identification)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Publish finding
    publish_parser = subparsers.add_parser("publish", help="Publish a finding")
    publish_parser.add_argument("title", help="Finding title")
    publish_parser.add_argument("content", nargs="?", help="Finding content")
    publish_parser.add_argument("-f", "--file", help="Read content from file")
    publish_parser.add_argument("-c", "--category", default="general",
                               help="Category (general, code, bug, solution, etc.)")
    publish_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    publish_parser.add_argument("--files", help="Comma-separated related files")
    publish_parser.add_argument("--confidence", type=float, default=1.0,
                               help="Confidence level (0.0 to 1.0)")
    publish_parser.set_defaults(func=publish_finding)
    
    # Discover findings
    discover_parser = subparsers.add_parser("discover", help="Discover findings")
    discover_parser.add_argument("-c", "--category", help="Filter by category")
    discover_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    discover_parser.add_argument("-l", "--limit", type=int, default=20,
                                help="Maximum results")
    discover_parser.set_defaults(func=discover_finding)
    
    # Search findings
    search_parser = subparsers.add_parser("search", help="Search findings")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-l", "--limit", type=int, default=20,
                              help="Maximum results")
    search_parser.set_defaults(func=search_findings)
    
    # Verify listeners
    verify_parser = subparsers.add_parser("verify", help="Verify other sessions are listening")
    verify_parser.set_defaults(func=verify_listeners)
    
    # Stats
    stats_parser = subparsers.add_parser("stats", help="Show session statistics")
    stats_parser.set_defaults(func=show_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
