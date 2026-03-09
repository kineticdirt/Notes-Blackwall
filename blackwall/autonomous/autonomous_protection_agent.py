"""
Autonomous protection agent.
Operates independently to protect content.
"""

from typing import Optional, Dict, List
from pathlib import Path
from .autonomous_agent import AutonomousAgent
from ..core.unified_processor import UnifiedProcessor
from ..database.registry import BlackwallRegistry


class AutonomousProtectionAgent(AutonomousAgent):
    """
    Autonomous agent that protects content independently.
    Makes its own decisions about what to protect and how.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        """Initialize autonomous protection agent."""
        super().__init__(agent_id=agent_id, agent_type="autonomous_protection")
        
        self.processor = UnifiedProcessor()
        self.registry = BlackwallRegistry()
        self.capabilities = ['protection', 'watermarking', 'poisoning', 'text', 'image']
        
        # Register with self-coordinator
        from .self_coordinator import SelfCoordinator
        coordinator = SelfCoordinator()
        coordinator.register_agent(
            self.agent_id,
            self.agent_type,
            self.capabilities
        )
    
    def _make_decision(self, context: Dict) -> str:
        """Autonomous decision-making for protection tasks."""
        if 'goal' in context:
            goal = context['goal']
            
            # Autonomous decision: what type of protection?
            if 'text' in goal.lower() or 'document' in goal.lower():
                return "Protect as text content"
            elif 'image' in goal.lower() or 'photo' in goal.lower():
                return "Protect as image content"
            else:
                return "Analyze content type and protect accordingly"
        
        return "Continue protection workflow"
    
    def autonomous_protect(self, content_path: str) -> Dict:
        """
        Autonomously protect content.
        Makes decisions about protection strategy.
        
        Args:
            content_path: Path to content
            
        Returns:
            Protection result
        """
        # Set autonomous goal
        goal_id = self.set_autonomous_goal(f"Protect content: {content_path}")
        
        # Autonomous decision: determine content type
        path = Path(content_path)
        if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            content_type = "image"
        else:
            content_type = "text"
        
        # Make decision
        decision = self.autonomous_decision({
            'goal': f"Protect {content_type} content",
            'content_path': content_path,
            'content_type': content_type
        })
        
        # Execute protection
        try:
            if content_type == "text":
                with open(content_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                protected_text, metadata = self.processor.process_text(text)
                
                output_path = str(path.with_suffix('.protected' + path.suffix))
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(protected_text)
                
                result = {
                    'success': True,
                    'output_path': output_path,
                    'uuid': metadata['uuid'],
                    'content_type': 'text'
                }
            else:
                output_path = str(path.with_suffix('.protected' + path.suffix))
                metadata = self.processor.process_image(content_path, output_path)
                
                result = {
                    'success': True,
                    'output_path': output_path,
                    'uuid': metadata['uuid'],
                    'content_type': 'image'
                }
            
            # Register
            self.registry.register_content(
                original_path=content_path,
                uuid=result['uuid'],
                content_type=content_type,
                processed_path=output_path,
                metadata=metadata
            )
            
            # Complete goal
            self.complete_goal(goal_id, result)
            
            return result
            
        except Exception as e:
            # Autonomous error handling
            self.autonomous_adapt({
                'success': False,
                'error': str(e),
                'context': {'content_path': content_path}
            })
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def autonomous_batch_protect(self, directory: str) -> Dict:
        """
        Autonomously protect all content in a directory.
        
        Args:
            directory: Directory to protect
            
        Returns:
            Batch protection results
        """
        goal_id = self.set_autonomous_goal(f"Batch protect directory: {directory}")
        
        dir_path = Path(directory)
        results = {
            'protected': [],
            'failed': [],
            'total': 0
        }
        
        # Autonomously find all content
        text_files = list(dir_path.rglob("*.txt")) + list(dir_path.rglob("*.md"))
        image_files = (list(dir_path.rglob("*.jpg")) + 
                      list(dir_path.rglob("*.png")) +
                      list(dir_path.rglob("*.webp")))
        
        all_files = text_files + image_files
        results['total'] = len(all_files)
        
        # Autonomously protect each file
        for file_path in all_files:
            result = self.autonomous_protect(str(file_path))
            if result.get('success'):
                results['protected'].append(result)
            else:
                results['failed'].append({
                    'path': str(file_path),
                    'error': result.get('error', 'Unknown')
                })
        
        # Complete goal
        self.complete_goal(goal_id, results)
        
        return results
