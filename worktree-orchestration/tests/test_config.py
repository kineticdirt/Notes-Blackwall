"""
Tests for configuration validation.
"""
import pytest
import json
from pathlib import Path
from src.config import ConfigValidator, Config


def test_valid_config(tmp_path):
    """Test validation of valid configuration."""
    config_file = tmp_path / "config.json"
    config_data = {
        "version": "2.0.0",
        "competition": {
            "name": "Test Competition",
            "rounds": 3,
            "max_competitors": 5
        },
        "worktree": {
            "base_path": "worktrees"
        },
        "arena": {
            "test_command": "pytest tests/",
            "timeout_seconds": 300
        }
    }
    config_file.write_text(json.dumps(config_data))
    
    validator = ConfigValidator()
    config = validator.validate(config_file)
    
    assert config.version == "2.0.0"
    assert config.competition.name == "Test Competition"
    assert config.competition.rounds == 3


def test_invalid_version(tmp_path):
    """Test rejection of invalid version."""
    config_file = tmp_path / "config.json"
    config_data = {
        "version": "1.0.0",  # Wrong version
        "competition": {
            "name": "Test",
            "rounds": 1,
            "max_competitors": 1
        },
        "worktree": {
            "base_path": "worktrees"
        },
        "arena": {
            "test_command": "pytest",
            "timeout_seconds": 300
        }
    }
    config_file.write_text(json.dumps(config_data))
    
    validator = ConfigValidator()
    with pytest.raises(ValueError):
        validator.validate(config_file)


def test_invalid_paths(tmp_path):
    """Test rejection of absolute paths."""
    config_file = tmp_path / "config.json"
    config_data = {
        "version": "2.0.0",
        "competition": {
            "name": "Test",
            "rounds": 1,
            "max_competitors": 1
        },
        "worktree": {
            "base_path": "/absolute/path"  # Invalid absolute path
        },
        "arena": {
            "test_command": "pytest",
            "timeout_seconds": 300
        }
    }
    config_file.write_text(json.dumps(config_data))
    
    validator = ConfigValidator()
    with pytest.raises(ValueError):
        validator.validate(config_file)
