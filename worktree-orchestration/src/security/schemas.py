"""
Security validation schemas using Pydantic.
"""
import re
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from pathlib import Path


class PathParam(BaseModel):
    """Safe path parameter."""
    path: str = Field(..., min_length=1, max_length=4096)
    
    @validator('path')
    def validate_path(cls, v):
        # Reject absolute paths
        if v.startswith('/'):
            raise ValueError('Absolute paths not allowed')
        
        # Reject path traversal
        if '..' in v:
            raise ValueError('Path traversal not allowed')
        
        # Reject control characters
        if any(ord(c) < 32 and c not in '\t\n\r' for c in v):
            raise ValueError('Control characters not allowed')
        
        # Reject null bytes
        if '\x00' in v:
            raise ValueError('Null bytes not allowed')
        
        return v
    
    def resolve(self, base: Path) -> Path:
        """Resolve path relative to base directory."""
        from .file_handling import SafePathHandler
        return SafePathHandler.validate_and_resolve(self.path, base)


class CompetitorIDParam(BaseModel):
    """Competitor ID parameter."""
    competitor_id: str = Field(..., min_length=1, max_length=50)
    
    @validator('competitor_id')
    def validate_id(cls, v):
        # Alphanumeric + underscore/hyphen only
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid competitor_id format: must be alphanumeric with underscores/hyphens')
        return v


class RoundNumParam(BaseModel):
    """Round number parameter."""
    round_num: int = Field(..., ge=1, le=1000)


class IPCRequest(BaseModel):
    """IPC request schema."""
    method: str = Field(..., min_length=1, max_length=100,
                        pattern=r'^[a-z_][a-z0-9_]*$')
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None
    
    @validator('method')
    def validate_method(cls, v):
        allowed_methods = {
            'start_round',
            'submit_solution',
            'submit_critique',
            'test_round',
            'end_round',
            'list_artifacts',
            'get_artifact',
            'list_rounds',
            'get_round_status',
        }
        if v not in allowed_methods:
            raise ValueError(f'Unknown method: {v}')
        return v


class SubmitSolutionRequest(BaseModel):
    """Submit solution request schema."""
    competitor_id: str = Field(..., min_length=1, max_length=50)
    round_num: int = Field(..., ge=1, le=1000)
    solution_path: PathParam
    
    @validator('competitor_id')
    def validate_competitor_id(cls, v):
        return CompetitorIDParam(competitor_id=v).competitor_id


class SubmitCritiqueRequest(BaseModel):
    """Submit critique request schema."""
    competitor_id: str = Field(..., min_length=1, max_length=50)
    round_num: int = Field(..., ge=1, le=1000)
    target_solution_id: str = Field(..., min_length=1, max_length=200)
    critique_path: PathParam
    
    @validator('competitor_id')
    def validate_competitor_id(cls, v):
        return CompetitorIDParam(competitor_id=v).competitor_id


class StartRoundRequest(BaseModel):
    """Start round request schema."""
    round_num: int = Field(..., ge=1, le=1000)


class TestRoundRequest(BaseModel):
    """Test round request schema."""
    round_num: int = Field(..., ge=1, le=1000)


class EndRoundRequest(BaseModel):
    """End round request schema."""
    round_num: int = Field(..., ge=1, le=1000)


class ListArtifactsRequest(BaseModel):
    """List artifacts request schema."""
    round_num: int = Field(..., ge=1, le=1000)


class GetArtifactRequest(BaseModel):
    """Get artifact request schema."""
    round_num: int = Field(..., ge=1, le=1000)
    artifact_type: str = Field(..., pattern=r'^(solutions|critiques)$')
    artifact_id: str = Field(..., min_length=1, max_length=200)
