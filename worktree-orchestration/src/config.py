"""
Configuration validation and management.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class CompetitionConfig(BaseModel):
    """Competition configuration."""
    name: str = Field(..., min_length=1, max_length=100)
    rounds: int = Field(..., ge=1, le=100)
    max_competitors: int = Field(..., ge=1, le=50)


class WorktreeConfig(BaseModel):
    """Worktree configuration."""
    base_path: str = Field(..., description="Relative path for worktree base")
    template_path: Optional[str] = Field(None, description="Optional template directory")
    cleanup_after_round: bool = Field(False, description="Auto-cleanup after round")
    
    @validator('base_path', 'template_path')
    def validate_relative_path(cls, v):
        if v is None:
            return v
        if v.startswith('/') or '..' in v:
            raise ValueError("Path must be relative and not contain '..'")
        return v


class ArenaConfig(BaseModel):
    """Arena configuration."""
    test_command: str = Field(..., min_length=1)
    timeout_seconds: int = Field(..., ge=1, le=3600)
    parallel_tests: bool = Field(False, description="Run tests in parallel")


class Config(BaseModel):
    """Main configuration."""
    version: str = Field(..., pattern=r'^2\.0\.0$')
    competition: CompetitionConfig
    worktree: WorktreeConfig
    arena: ArenaConfig


class ConfigValidator:
    """Validates competition configuration."""
    
    @staticmethod
    def validate(config_path: Path) -> Config:
        """
        Validate configuration file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            Validated Config object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        
        try:
            return Config(**data)
        except Exception as e:
            raise ValueError(f"Config validation failed: {e}")
    
    @staticmethod
    def validate_paths(config: Config, base_dir: Path) -> None:
        """
        Validate that all paths in config exist (if specified).
        
        Args:
            config: Validated config
            base_dir: Base directory for relative paths
            
        Raises:
            ValueError: If any path is invalid
        """
        worktree_base = base_dir / config.worktree.base_path
        if worktree_base.exists() and not worktree_base.is_dir():
            raise ValueError(f"Worktree base path exists but is not a directory: {worktree_base}")
        
        if config.worktree.template_path:
            template_path = base_dir / config.worktree.template_path
            if not template_path.exists():
                raise ValueError(f"Template path does not exist: {template_path}")
            if not template_path.is_dir():
                raise ValueError(f"Template path is not a directory: {template_path}")
