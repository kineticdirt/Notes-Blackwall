"""
Detection agent - detects watermarks in content using Blackwall tools.
"""

from typing import Optional, List, Dict
from pathlib import Path
from agents.mcp_aware_agent import MCPAwareAgent
from core.unified_processor import UnifiedProcessor
from database.registry import BlackwallRegistry


class DetectionAgent(MCPAwareAgent):
    """
    Agent specialized in detecting watermarks in content.
    Uses Blackwall's detection capabilities and MCP tools.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """Initialize detection agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="detection",
            ledger_path=ledger_path
        )
        
        self.processor = UnifiedProcessor()
        self.registry = BlackwallRegistry()
        self.metadata = {
            "specialization": "watermark_detection",
            "capabilities": ["detect_text", "detect_image", "scan_directory"]
        }
    
    def detect_watermark(self, content_path: str, content_type: str = "auto") -> Dict:
        """
        Detect watermark in content.
        
        Args:
            content_path: Path to content file
            content_type: "text", "image", or "auto"
            
        Returns:
            Detection result dictionary
        """
        intent = self.declare_intent(
            f"Detecting watermark in: {content_path}",
            resources=[content_path]
        )
        
        self.log(f"Detecting watermark in {content_path}")
        
        # Auto-detect type
        if content_type == "auto":
            path = Path(content_path)
            if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                content_type = "image"
            else:
                content_type = "text"
        
        # Detect
        if content_type == "text":
            # Read file using MCP tool
            with open(content_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            result = self.processor.detect_text(text)
        else:
            result = self.processor.detect_image(content_path)
        
        # Look up in registry if UUID found
        if result['detected'] and result['uuid']:
            registry_entry = self.registry.lookup_by_uuid(result['uuid'])
            result['registry_match'] = registry_entry
        
        # Log detection
        if result['detected']:
            self.log(f"Watermark detected! UUID: {result['uuid']}", message_type="success")
        else:
            self.log("No watermark detected", message_type="info")
        
        return result
    
    def scan_directory(self, directory: str, content_type: str = "auto") -> List[Dict]:
        """
        Scan directory for watermarked content.
        
        Args:
            directory: Directory to scan
            content_type: Filter by type ("text", "image", or "auto" for both)
            
        Returns:
            List of detection results
        """
        intent = self.declare_intent(
            f"Scanning directory: {directory}",
            resources=[directory]
        )
        
        self.log(f"Scanning directory: {directory}")
        
        # Use MCP tool to list directory
        # In actual implementation, would use list_dir tool
        from pathlib import Path
        dir_path = Path(directory)
        
        results = []
        
        # Find files
        if content_type == "text" or content_type == "auto":
            text_files = list(dir_path.rglob("*.txt")) + list(dir_path.rglob("*.md"))
            for file in text_files:
                try:
                    result = self.detect_watermark(str(file), "text")
                    if result['detected']:
                        results.append(result)
                except Exception as e:
                    self.log(f"Error scanning {file}: {e}", message_type="error")
        
        if content_type == "image" or content_type == "auto":
            image_files = (list(dir_path.rglob("*.jpg")) + 
                          list(dir_path.rglob("*.jpeg")) +
                          list(dir_path.rglob("*.png")) +
                          list(dir_path.rglob("*.webp")))
            for file in image_files:
                try:
                    result = self.detect_watermark(str(file), "image")
                    if result['detected']:
                        results.append(result)
                except Exception as e:
                    self.log(f"Error scanning {file}: {e}", message_type="error")
        
        self.log(f"Scan complete: {len(results)} watermarks found")
        return results
