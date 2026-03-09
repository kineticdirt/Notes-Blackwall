"""
Kanban Board: AI-native Kanban board system.
Uses markdown files that AIs can directly read and write.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum


class CardStatus(Enum):
    """Card status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass
class KanbanCard:
    """A card in the Kanban board."""
    card_id: str
    title: str
    description: str = ""
    status: str = CardStatus.TODO.value
    assignee: Optional[str] = None  # Agent/session ID
    tags: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10, higher = more important
    created_at: str = ""
    updated_at: str = ""
    due_date: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    related_resources: List[str] = field(default_factory=list)  # Links to markdown files
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
    
    def to_markdown(self) -> str:
        """Convert card to markdown format."""
        lines = [
            f"## {self.title}",
            f"**ID**: `{self.card_id}`",
            f"**Status**: {self.status}",
            f"**Priority**: {self.priority}/10",
        ]
        
        if self.assignee:
            lines.append(f"**Assignee**: {self.assignee}")
        
        if self.tags:
            lines.append(f"**Tags**: {', '.join(self.tags)}")
        
        if self.due_date:
            lines.append(f"**Due**: {self.due_date}")
        
        if self.description:
            lines.append(f"\n{self.description}")
        
        if self.related_resources:
            lines.append("\n### Related Resources")
            for resource in self.related_resources:
                lines.append(f"- [{resource}]({resource})")
        
        if self.metadata:
            lines.append(f"\n**Metadata**: {json.dumps(self.metadata, indent=2)}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, content: str, card_id: Optional[str] = None) -> 'KanbanCard':
        """Parse card from markdown."""
        lines = content.split('\n')
        
        # Extract title
        title = ""
        description_lines = []
        in_description = False
        
        for line in lines:
            if line.startswith('## '):
                title = line[3:].strip()
            elif line.startswith('**ID**:'):
                if not card_id:
                    card_id = line.split('`')[1] if '`' in line else None
            elif line.startswith('**Status**:'):
                status = line.split('**Status**:')[1].strip()
            elif line.startswith('**Priority**:'):
                priority = int(line.split('/')[0].split(':')[1].strip())
            elif line.startswith('**Assignee**:'):
                assignee = line.split('**Assignee**:')[1].strip()
            elif line.startswith('**Tags**:'):
                tags_str = line.split('**Tags**:')[1].strip()
                tags = [t.strip() for t in tags_str.split(',')]
            elif line.strip() and not line.startswith('**') and not line.startswith('###'):
                if title:  # After title, this is description
                    description_lines.append(line)
        
        return cls(
            card_id=card_id or f"card-{uuid.uuid4().hex[:12]}",
            title=title or "Untitled",
            description="\n".join(description_lines).strip(),
            status=status if 'status' in locals() else CardStatus.TODO.value,
            assignee=assignee if 'assignee' in locals() else None,
            tags=tags if 'tags' in locals() else [],
            priority=priority if 'priority' in locals() else 5
        )


@dataclass
class KanbanColumn:
    """A column in the Kanban board."""
    name: str
    status: str
    cards: List[KanbanCard] = field(default_factory=list)
    limit: Optional[int] = None  # WIP limit
    
    def add_card(self, card: KanbanCard):
        """Add card to column."""
        if self.limit and len(self.cards) >= self.limit:
            raise ValueError(f"Column {self.name} has reached WIP limit of {self.limit}")
        self.cards.append(card)
    
    def remove_card(self, card_id: str) -> Optional[KanbanCard]:
        """Remove card from column."""
        for i, card in enumerate(self.cards):
            if card.card_id == card_id:
                return self.cards.pop(i)
        return None


class KanbanBoard:
    """
    Kanban Board in AI-native language.
    Uses markdown files that AIs can directly read and write.
    """
    
    def __init__(self, board_id: str, name: str, base_path: Optional[Path] = None):
        """
        Initialize Kanban board.
        
        Args:
            board_id: Unique board identifier
            name: Board name
            base_path: Base path for board files (defaults to .kanban/{board_id})
        """
        self.board_id = board_id
        self.name = name
        self.base_path = base_path or Path(".kanban") / board_id
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Columns
        self.columns: Dict[str, KanbanColumn] = {
            "todo": KanbanColumn("To Do", CardStatus.TODO.value),
            "in_progress": KanbanColumn("In Progress", CardStatus.IN_PROGRESS.value, limit=5),
            "review": KanbanColumn("Review", CardStatus.REVIEW.value),
            "done": KanbanColumn("Done", CardStatus.DONE.value),
        }
        
        # Cards
        self.cards: Dict[str, KanbanCard] = {}
        
        # Load from markdown if exists
        self._load_from_markdown()
    
    def _load_from_markdown(self):
        """Load board from markdown files."""
        board_file = self.base_path / "board.md"
        if board_file.exists():
            self._parse_markdown(board_file.read_text())
    
    def _parse_markdown(self, content: str):
        """Parse markdown board content."""
        # Simple parser - can be enhanced
        sections = content.split('\n## ')
        for section in sections[1:]:  # Skip first empty section
            card = KanbanCard.from_markdown('## ' + section)
            self.add_card(card)
    
    def add_card(self, card: KanbanCard, column_name: Optional[str] = None):
        """
        Add card to board.
        
        Args:
            card: Card to add
            column_name: Column name (defaults to card status)
        """
        self.cards[card.card_id] = card
        
        # Add to appropriate column
        column_name = column_name or card.status
        if column_name in self.columns:
            self.columns[column_name].add_card(card)
        
        # Save to markdown
        self._save_to_markdown()
    
    def move_card(self, card_id: str, new_status: str):
        """Move card to new status/column."""
        if card_id not in self.cards:
            raise ValueError(f"Card {card_id} not found")
        
        card = self.cards[card_id]
        old_status = card.status
        
        # Remove from old column
        if old_status in self.columns:
            self.columns[old_status].remove_card(card_id)
        
        # Update card status
        card.status = new_status
        card.updated_at = datetime.now().isoformat()
        
        # Add to new column
        if new_status in self.columns:
            self.columns[new_status].add_card(card)
        
        # Save to markdown
        self._save_to_markdown()
    
    def get_card(self, card_id: str) -> Optional[KanbanCard]:
        """Get card by ID."""
        return self.cards.get(card_id)
    
    def get_cards_by_status(self, status: str) -> List[KanbanCard]:
        """Get all cards with given status."""
        return [card for card in self.cards.values() if card.status == status]
    
    def get_cards_by_assignee(self, assignee: str) -> List[KanbanCard]:
        """Get all cards assigned to agent."""
        return [card for card in self.cards.values() if card.assignee == assignee]
    
    def to_markdown(self) -> str:
        """Convert board to markdown format."""
        lines = [
            f"# {self.name}",
            f"**Board ID**: `{self.board_id}`",
            f"**Updated**: {datetime.now().isoformat()}",
            "",
            "## Columns"
        ]
        
        for column_name, column in self.columns.items():
            lines.append(f"\n### {column.name} ({len(column.cards)} cards)")
            if column.limit:
                lines.append(f"*WIP Limit: {column.limit}*")
            
            for card in column.cards:
                lines.append("")
                lines.append(card.to_markdown())
        
        return "\n".join(lines)
    
    def _save_to_markdown(self):
        """Save board to markdown file."""
        board_file = self.base_path / "board.md"
        board_file.write_text(self.to_markdown())
        
        # Also save individual card files
        cards_dir = self.base_path / "cards"
        cards_dir.mkdir(exist_ok=True)
        
        for card_id, card in self.cards.items():
            card_file = cards_dir / f"{card_id}.md"
            card_file.write_text(card.to_markdown())
    
    def get_summary(self) -> Dict:
        """Get board summary."""
        return {
            "board_id": self.board_id,
            "name": self.name,
            "total_cards": len(self.cards),
            "columns": {
                name: {
                    "name": col.name,
                    "card_count": len(col.cards),
                    "wip_limit": col.limit
                }
                for name, col in self.columns.items()
            }
        }
