#!/usr/bin/env python3
"""
Kanban Board Manager for Website Proxy Project
Manages project memory and tracks all discussed topics.
"""

import sys
import uuid
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.kanban.kanban_board import KanbanBoard, KanbanCard


class ProjectKanbanManager:
    """Manages kanban board for website proxy project."""
    
    def __init__(self, board_id: str = "website-proxy", board_path: Path = None):
        """Initialize kanban manager."""
        if board_path is None:
            board_path = Path(__file__).parent / ".kanban" / board_id
        
        self.board = KanbanBoard(board_id, "Website Proxy Project", base_path=board_path)
        self._initialize_board()
    
    def _initialize_board(self):
        """Initialize board with default columns and cards."""
        # Add initial cards if board is empty
        if len(self.board.cards) == 0:
            self._add_initial_cards()
    
    def _add_initial_cards(self):
        """Add initial cards based on project_kanban.md."""
        # Done items
        done_items = [
            ("Core Infrastructure", "FastAPI proxy server, persistent cache, multi-level caching"),
            ("Browser Integration", "Playwright support, browser-like headers, cookie management"),
            ("Compliance & Standards", "User-Agent policy, robots.txt, rate limiting, compression"),
            ("Testing & Validation", "Tested with multiple websites, cache performance validated"),
            ("Pre/Post Processing Integration", "Integrated existing advanced_theme.py, grainrad effects working"),
            ("Shader Effects", "Scanlines, grain, noise, CSS-based shader effects"),
            ("Dithering & ASCII", "Floyd-Steinberg dithering, ASCII conversion using existing code"),
        ]
        
        for title, description in done_items:
            card = KanbanCard(
                card_id=f"card-{uuid.uuid4().hex[:8]}",
                title=title,
                description=description,
                status="done",
                priority=5
            )
            self.board.add_card(card)
        
        # In Progress
        in_progress = [
            ("Effects Integration Testing", "Testing grainrad effects on real websites, verifying visual output"),
        ]
        
        for title, description in in_progress:
            card = KanbanCard(
                card_id=f"card-{uuid.uuid4().hex[:8]}",
                title=title,
                description=description,
                status="in_progress",
                priority=8
            )
            self.board.add_card(card)
        
        # Backlog
        backlog_items = [
            ("Research postprocessing library", "Study pmndrs/postprocessing API and effects"),
            ("Study Book of Shaders", "Learn fragment shader techniques"),
            ("Study Efecto (Codrops)", "Real-time ASCII and dithering with WebGL shaders"),
            ("Implement pre-processing", "Image preparation, pixelation, luminance calculation"),
            ("Implement dithering algorithms", "Floyd-Steinberg, Atkinson, Jarvis-Judice-Ninke, etc."),
            ("Implement ASCII conversion", "Procedural character drawing on GPU"),
            ("Implement post-processing", "Bloom, scanlines, curvature, chromatic aberration, vignette"),
            ("Create color palettes", "Game Boy, synthwave, noir, amber, cyberpunk, etc."),
            ("Design shader pipeline", "Architecture for shader processing"),
            ("Add shader UI controls", "Real-time preview and presets"),
        ]
        
        for title, description in backlog_items:
            card = KanbanCard(
                card_id=f"card-{uuid.uuid4().hex[:8]}",
                title=title,
                description=description,
                status="todo",
                priority=5
            )
            self.board.add_card(card)
    
    def add_topic(self, title: str, description: str = "", status: str = "todo", priority: int = 5):
        """Add a new topic to the board."""
        card = KanbanCard(
            card_id=f"card-{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            status=status,
            priority=priority
        )
        self.board.add_card(card)
        return card
    
    def get_all_topics(self):
        """Get all topics organized by status."""
        cards = list(self.board.cards.values())
        organized = {
            "todo": [],
            "in_progress": [],
            "done": [],
            "blocked": []
        }
        
        for card in cards:
            status = card.status or "todo"
            if status in organized:
                organized[status].append(card)
            else:
                organized["todo"].append(card)
        
        return organized
    
    def print_board(self):
        """Print kanban board to console."""
        topics = self.get_all_topics()
        
        print("=" * 70)
        print("WEBSITE PROXY PROJECT - KANBAN BOARD")
        print("=" * 70)
        print()
        
        status_map = {
            "in_progress": "In Progress",
            "done": "Done",
            "todo": "Backlog",
            "blocked": "Blocked"
        }
        
        for status_key, status_name in status_map.items():
            cards = topics[status_key]
            if cards:
                print(f"\n## {status_name}")
                print("-" * 70)
                for card in sorted(cards, key=lambda c: c.priority, reverse=True):
                    print(f"  [{card.priority}] {card.title}")
                    if card.description:
                        print(f"      {card.description[:60]}...")
                print()
    
    def export_markdown(self, output_path: Path = None):
        """Export kanban board to markdown."""
        if output_path is None:
            output_path = Path(__file__).parent / "project_kanban.md"
        
        topics = self.get_all_topics()
        
        lines = ["# Website Proxy & Reinterpretation Project - Kanban Board\n"]
        
        status_map = {
            "todo": ("Backlog", False),
            "in_progress": ("In Progress", False),
            "done": ("Done", True),
            "blocked": ("Blocked", False)
        }
        
        for status_key, (status_name, is_done) in status_map.items():
            cards = topics[status_key]
            lines.append(f"\n## {status_name}\n")
            
            if not cards:
                lines.append("_No items_\n")
            else:
                for card in sorted(cards, key=lambda c: c.priority, reverse=True):
                    checkbox = "- [x]" if is_done else "- [ ]"
                    lines.append(f"{checkbox} **{card.title}**")
                    if card.description:
                        lines.append(f"  - {card.description}")
                    lines.append("")
        
        output_path.write_text("\n".join(lines))
        print(f"Exported kanban board to: {output_path}")


def main():
    """Main function."""
    manager = ProjectKanbanManager()
    
    # Print current board
    manager.print_board()
    
    # Export to markdown
    manager.export_markdown()
    
    print("\n" + "=" * 70)
    print("Kanban board management complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
