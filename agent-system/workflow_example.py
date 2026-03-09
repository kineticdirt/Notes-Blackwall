"""
Example workflow: Cleanup -> Test -> Documentation
"""

from workflow_coordinator import WorkflowCoordinator


def example_basic_workflow():
    """Run basic workflow on a codebase."""
    
    # Initialize workflow coordinator
    workflow = WorkflowCoordinator()
    
    # Run full workflow
    target_path = "nightshade-tracker"
    files_to_process = [
        "core/watermarking.py",
        "core/poisoning.py",
        "core/optimizer.py"
    ]
    
    print("Starting workflow: Cleanup -> Test -> Documentation")
    print(f"Target: {target_path}")
    print(f"Files: {files_to_process}\n")
    
    # Run workflow
    workflow.run_full_workflow(target_path, files_to_process)
    
    # Check status
    status = workflow.get_workflow_status()
    print("\n=== Workflow Status ===")
    print(f"Status: {status['status']}")
    print(f"\nScratchpad Entries:")
    for section, count in status['scratchpad_sections'].items():
        print(f"  {section}: {count} entries")
    
    # View scratchpad
    print("\n=== Scratchpad Overview ===")
    scratchpad = workflow.view_scratchpad("overview")
    for entry in scratchpad.get("overview", [])[-5:]:
        print(f"[{entry['agent_id']}] {entry['content']}")
    
    print("\n=== Code Notes ===")
    code_notes = workflow.view_scratchpad("code_notes")
    for entry in code_notes.get("code_notes", [])[-3:]:
        print(f"[{entry['agent_id']}] {entry['content']}")
    
    print("\n=== Test Notes ===")
    test_notes = workflow.view_scratchpad("test_notes")
    for entry in test_notes.get("test_notes", [])[-3:]:
        print(f"[{entry['agent_id']}] {entry['content']}")
    
    print("\n=== Documentation Notes ===")
    doc_notes = workflow.view_scratchpad("doc_notes")
    for entry in doc_notes.get("doc_notes", [])[-3:]:
        print(f"[{entry['agent_id']}] {entry['content']}")


def example_step_by_step():
    """Run workflow step by step with manual control."""
    
    workflow = WorkflowCoordinator()
    
    # Step 1: Cleanup only
    print("=== Step 1: Cleanup ===")
    workflow._run_cleanup_phase("nightshade-tracker", ["core/watermarking.py"])
    
    # View what cleanup agent found
    code_notes = workflow.view_scratchpad("code_notes")
    print("\nCleanup Agent Notes:")
    for entry in code_notes.get("code_notes", []):
        print(f"  - {entry['content']}")
    
    # Step 2: Tests (uses cleanup notes)
    print("\n=== Step 2: Testing ===")
    workflow._run_test_phase("nightshade-tracker", ["core/watermarking.py"])
    
    # Step 3: Documentation (uses all notes)
    print("\n=== Step 3: Documentation ===")
    workflow._run_doc_phase("nightshade-tracker", ["core/watermarking.py"])
    
    # Final summary
    print("\n=== Final Scratchpad ===")
    all_notes = workflow.view_scratchpad()
    print(f"Total entries across all sections: {sum(len(v) if isinstance(v, list) else 0 for v in all_notes.get('sections', {}).values())}")


if __name__ == "__main__":
    print("=" * 60)
    print("WORKFLOW EXAMPLE: Cleanup -> Test -> Documentation")
    print("=" * 60)
    
    print("\n1. Running basic workflow...")
    example_basic_workflow()
    
    print("\n\n" + "=" * 60)
    print("2. Running step-by-step workflow...")
    print("=" * 60)
    example_step_by_step()
