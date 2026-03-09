"""
Setup script for Claude integration (LSP and subagents).
"""

from pathlib import Path
from lsp_manager import LSPManager
import json


def setup_claude_integration(project_path: str = "."):
    """
    Setup Claude integration for a project.
    
    Args:
        project_path: Path to project directory
    """
    print("=" * 60)
    print("Claude Integration Setup")
    print("=" * 60)
    
    # Initialize LSP manager
    lsp_manager = LSPManager()
    
    # Detect languages
    print("\n1. Detecting project languages...")
    languages = lsp_manager.detect_project_languages(project_path)
    
    if languages:
        print(f"   Detected: {', '.join(languages)}")
    else:
        print("   No languages detected")
        return
    
    # Check LSP status
    print("\n2. Checking LSP status...")
    required = lsp_manager.get_required_lsps(languages)
    
    for req in required:
        status = lsp_manager.check_lsp_status(req["language"])
        if status["binary_available"]:
            print(f"   ✅ {req['language']}: {req['binary']} available")
        else:
            print(f"   ❌ {req['language']}: {req['binary']} missing")
            print(f"      Install: {status.get('install_command', 'N/A')}")
    
    # Generate installation commands
    print("\n3. Claude Plugin Installation Commands:")
    print("   (Run these in Claude Code)")
    print()
    
    install_commands = lsp_manager.get_installation_commands(languages)
    for cmd in install_commands:
        print(f"   {cmd}")
    
    # Create setup guide
    print("\n4. Creating setup guide...")
    guide_path = Path(project_path) / "LSP_SETUP.md"
    
    guide_content = lsp_manager.generate_installation_script(languages)
    guide_content += "\n\n# Claude Plugin Commands\n\n"
    guide_content += "Run these in Claude Code:\n\n"
    for cmd in install_commands:
        guide_content += f"```\n{cmd}\n```\n\n"
    
    with open(guide_path, 'w') as f:
        f.write(guide_content)
    
    print(f"   Created: {guide_path}")
    
    # Verify subagents
    print("\n5. Checking subagent configuration...")
    agents_dir = Path(project_path) / ".claude" / "agents"
    
    if agents_dir.exists():
        agents = list(agents_dir.glob("*.md"))
        print(f"   Found {len(agents)} subagent(s):")
        for agent in agents:
            print(f"   - {agent.name}")
    else:
        print("   No subagents configured")
        print(f"   Create subagents in: {agents_dir}")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install language server binaries (see LSP_SETUP.md)")
    print("2. Install Claude plugins (commands above)")
    print("3. Restart Claude Code")
    print("4. Run workflow with: EnhancedWorkflowCoordinator")


if __name__ == "__main__":
    setup_claude_integration(".")
