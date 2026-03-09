"""
Protection agent - handles content protection (text + images) using Blackwall tools.
"""

from typing import Optional, List
from agents.mcp_aware_agent import MCPAwareAgent
from core.unified_processor import UnifiedProcessor
from database.registry import BlackwallRegistry


class ProtectionAgent(MCPAwareAgent):
    """
    Agent specialized in protecting content (text and images).
    Uses Blackwall's unified processor and MCP tools.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """Initialize protection agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="protection",
            ledger_path=ledger_path
        )
        
        self.processor = UnifiedProcessor()
        self.registry = BlackwallRegistry()
        self.metadata = {
            "specialization": "content_protection",
            "capabilities": ["protect_text", "protect_image", "poison", "watermark"]
        }
    
    def protect_content(self, content_path: str, content_type: str = "auto") -> Dict:
        """
        Protect content (text or image) using Blackwall.
        
        Args:
            content_path: Path to content file
            content_type: "text", "image", or "auto"
            
        Returns:
            Protection result dictionary
        """
        # Declare intent
        intent = self.declare_intent(
            f"Protecting content: {content_path}",
            resources=[content_path]
        )
        
        self.log(f"Starting protection for {content_path}")
        
        # Auto-detect type if needed
        if content_type == "auto":
            path = Path(content_path)
            if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                content_type = "image"
            else:
                content_type = "text"
        
        # Use MCP tools to read file
        if content_type == "text":
            # Read text file using MCP tool
            result = self.use_tool("read_file", target_file=content_path)
            # In actual implementation, would get file content from result
            # For now, read directly
            with open(content_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Process
            protected_text, metadata = self.processor.process_text(text)
            
            # Write protected file using MCP tool
            output_path = str(Path(content_path).with_suffix('.protected' + Path(content_path).suffix))
            self.use_tool("write_file", file_path=output_path, contents=protected_text)
            
            # Register
            self.registry.register_content(
                original_path=content_path,
                uuid=metadata['uuid'],
                content_type="text",
                processed_path=output_path,
                metadata=metadata
            )
            
            return {
                "success": True,
                "content_type": "text",
                "output_path": output_path,
                "uuid": metadata['uuid']
            }
        
        else:  # image
            # Process image
            output_path = str(Path(content_path).with_suffix('.protected' + Path(content_path).suffix))
            metadata = self.processor.process_image(content_path, output_path)
            
            # Register
            self.registry.register_content(
                original_path=content_path,
                uuid=metadata['uuid'],
                content_type="image",
                processed_path=output_path,
                metadata=metadata
            )
            
            return {
                "success": True,
                "content_type": "image",
                "output_path": output_path,
                "uuid": metadata['uuid']
            }
    
    def batch_protect(self, content_paths: List[str]) -> List[Dict]:
        """Protect multiple content files."""
        results = []
        for path in content_paths:
            try:
                result = self.protect_content(path)
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "path": path,
                    "error": str(e)
                })
        return results
