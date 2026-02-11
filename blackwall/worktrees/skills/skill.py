"""
Skill: A capability that can be assigned to agents.
Skills are defined in nested markdown files with YAML frontmatter.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


@dataclass
class Skill:
    """
    Represents a skill that can be used by agents.
    Skills are loaded from nested markdown files.
    """
    name: str
    description: str
    version: str = "1.0.0"
    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    workflow: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    file_path: Optional[Path] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert skill to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tools": self.tools,
            "resources": self.resources,
            "workflow": self.workflow,
            "examples": self.examples,
            "metadata": self.metadata,
            "file_path": str(self.file_path) if self.file_path else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Skill':
        """Create skill from dictionary."""
        file_path = data.get("file_path")
        if file_path:
            file_path = Path(file_path)
        
        return cls(
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            tools=data.get("tools", []),
            resources=data.get("resources", []),
            workflow=data.get("workflow", []),
            examples=data.get("examples", []),
            metadata=data.get("metadata", {}),
            file_path=file_path,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )
