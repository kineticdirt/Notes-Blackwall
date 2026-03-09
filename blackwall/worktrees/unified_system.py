"""
Unified System: Integrates all components from whiteboard design.
- Kanban Board (AI-native)
- MCP UI (nested markdown)
- Resources (markdown + DB)
- Workflows (Airflow-style)
- Worktrees (agent organization)
"""

from typing import Dict, Optional
from pathlib import Path

from .kanban import KanbanBoard, KanbanDatabase
from .mcp_ui import MCPUILoader
from .workflows import WorkflowEngine
from .worktree_manager import UnifiedWorktreeManager
from .cross_chat import CrossChatBridge
from .coordination_integration import CoordinatedCrossChatBridge


class UnifiedMCPSystem:
    """
    Unified system integrating all whiteboard components:
    1. Kanban Board in AI native language
    2. MCP UI with nested markdown files
    3. Resources pointing to nested markdown + DB
    4. Airflow-style workflows
    5. Worktrees for organizing agents
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize unified system.
        
        Args:
            base_path: Base path for all system files
        """
        if base_path is None:
            base_path = Path(".")
        
        self.base_path = Path(base_path)
        
        # Initialize components
        self.worktree_manager = UnifiedWorktreeManager(base_path=self.base_path / ".worktrees")
        self.kanban_db = KanbanDatabase(db_path=self.base_path / ".kanban" / "kanban.db")
        self.workflow_engine = WorkflowEngine(base_path=self.base_path / ".workflows")
        self.mcp_ui_loader = MCPUILoader(ui_path=self.base_path / ".mcp-ui")
        
        # Cross-chat bridge
        self.cross_chat = CoordinatedCrossChatBridge()
    
    def create_kanban_board(self, board_id: str, name: str) -> KanbanBoard:
        """Create a new Kanban board."""
        board = KanbanBoard(board_id, name, base_path=self.base_path / ".kanban" / board_id)
        self.kanban_db.save_board(board_id, name)
        return board
    
    def get_kanban_board(self, board_id: str) -> Optional[KanbanBoard]:
        """Get Kanban board by ID."""
        board_path = self.base_path / ".kanban" / board_id / "board.md"
        if board_path.exists():
            return KanbanBoard(board_id, "", base_path=board_path.parent)
        return None
    
    def create_workflow_dag(self, dag_id: str, description: str):
        """Create a workflow DAG."""
        from .workflows import WorkflowDAG
        dag = WorkflowDAG(dag_id=dag_id, description=description)
        self.workflow_engine.register_dag(dag)
        return dag
    
    def get_ui_tree(self) -> Dict:
        """Get MCP UI tree."""
        return self.mcp_ui_loader.get_ui_tree()
    
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        return {
            "worktrees": len(self.worktree_manager.list_all_worktrees()),
            "kanban_boards": len(list((self.base_path / ".kanban").glob("*/board.md"))),
            "workflows": len(self.workflow_engine.dags),
            "ui_components": len(self.mcp_ui_loader.components),
            "cross_chat_sessions": len(self.cross_chat.verify_listeners()["listeners"])
        }


def create_unified_system(base_path: Optional[Path] = None) -> UnifiedMCPSystem:
    """
    Create unified MCP system.
    
    Args:
        base_path: Base path for system files
        
    Returns:
        UnifiedMCPSystem instance
    """
    return UnifiedMCPSystem(base_path=base_path)
