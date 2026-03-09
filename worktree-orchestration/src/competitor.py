"""
Competitor registration and management.
"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class Competitor(BaseModel):
    """Represents a competitor."""
    competitor_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., min_length=1, max_length=100)
    script_path: Path = Field(..., description="Path to competitor script")
    registered_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @validator('competitor_id')
    def validate_id(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("competitor_id must be alphanumeric with underscores/hyphens")
        if len(v) > 50:
            raise ValueError("competitor_id must be <= 50 characters")
        return v


class CompetitorRegistry:
    """Manages competitor registration."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.competitors_dir = cache_dir / "competitors"
        self.competitors_dir.mkdir(parents=True, exist_ok=True)
    
    def register_competitor(self, name: str, script_path: Path, base_dir: Path) -> Competitor:
        """
        Register a new competitor.
        
        Args:
            name: Human-readable competitor name
            script_path: Path to competitor script (relative to base_dir)
            base_dir: Base directory for resolving relative paths
            
        Returns:
            Competitor object
            
        Raises:
            ValueError: If validation fails
            FileNotFoundError: If script doesn't exist
        """
        # Generate competitor ID from name
        competitor_id = name.lower().replace(' ', '_').replace('-', '_')
        competitor_id = ''.join(c for c in competitor_id if c.isalnum() or c == '_')
        
        # Resolve script path
        if not script_path.is_absolute():
            script_path = base_dir / script_path
        
        # Validate script exists
        if not script_path.exists():
            raise FileNotFoundError(f"Competitor script not found: {script_path}")
        
        # Check if already registered
        competitor_file = self.competitors_dir / f"{competitor_id}.json"
        if competitor_file.exists():
            raise ValueError(f"Competitor already registered: {competitor_id}")
        
        # Create competitor
        competitor = Competitor(
            competitor_id=competitor_id,
            name=name,
            script_path=script_path
        )
        
        # Save to disk
        with open(competitor_file, 'w') as f:
            json.dump(competitor.dict(), f, indent=2, default=str)
        
        return competitor
    
    def get_competitor(self, competitor_id: str) -> Optional[Competitor]:
        """
        Get competitor by ID.
        
        Args:
            competitor_id: Competitor identifier
            
        Returns:
            Competitor if found, None otherwise
        """
        competitor_file = self.competitors_dir / f"{competitor_id}.json"
        if not competitor_file.exists():
            return None
        
        try:
            with open(competitor_file, 'r') as f:
                data = json.load(f)
            return Competitor(**data)
        except Exception:
            return None
    
    def list_competitors(self) -> List[Competitor]:
        """
        List all registered competitors.
        
        Returns:
            List of Competitor objects
        """
        competitors = []
        
        for competitor_file in self.competitors_dir.glob("*.json"):
            try:
                with open(competitor_file, 'r') as f:
                    data = json.load(f)
                competitors.append(Competitor(**data))
            except Exception:
                continue
        
        return sorted(competitors, key=lambda c: c.registered_at)
