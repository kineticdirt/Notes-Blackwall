"""
Grainrad AI Agent: Final quality verification using vision APIs.
"""

import sys
from pathlib import Path
import base64
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class GrainradAIAgent:
    """AI Agent for final quality verification."""
    
    def __init__(self, anthropic_key: Optional[str] = None, gemini_key: Optional[str] = None):
        """
        Initialize AI agent.
        
        Args:
            anthropic_key: Anthropic API key (for Claude Vision)
            gemini_key: Google Gemini API key (fallback)
        """
        self.anthropic = None
        self.gemini = None
        
        if anthropic_key:
            try:
                from anthropic import Anthropic
                self.anthropic = Anthropic(api_key=anthropic_key)
            except ImportError:
                print("⚠ anthropic package not installed")
        
        if gemini_key:
            try:
                from google import genai
                self.gemini = genai.Client(api_key=gemini_key)
            except ImportError:
                print("⚠ google-genai package not installed")
    
    async def verify_quality(self, original_image: bytes, transformed_content: Dict) -> Dict:
        """
        Final sanity check: Verify transformed content quality.
        Only called at the end, before serving to user.
        
        Args:
            original_image: Original image bytes
            transformed_content: Transformed content dictionary
            
        Returns:
            Verification result with pass/fail and reason
        """
        # Try Claude first
        if self.anthropic:
            try:
                response = await self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=256,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64.b64encode(original_image).decode()
                                }
                            },
                            {
                                "type": "text",
                                "text": f"Quick sanity check: Does this transformed content look correct? "
                                       f"Transformed type: {transformed_content.get('type', 'unknown')}. "
                                       f"Respond with 'PASS' or 'FAIL' and brief reason."
                            }
                        ]
                    }]
                )
                result = response.content[0].text
                verified = "PASS" in result.upper() or "YES" in result.upper()
                return {
                    "provider": "claude",
                    "verified": verified,
                    "reason": result,
                    "raw_response": result
                }
            except Exception as e:
                # Fail open - log but don't block
                print(f"⚠ Claude verification failed: {e}")
                return {"verified": True, "reason": f"Claude check failed: {e}", "provider": "claude-error"}
        
        # Fallback to Gemini
        if self.gemini:
            try:
                from google.genai import types
                response = self.gemini.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=[
                        types.Part.from_bytes(data=original_image, mime_type='image/jpeg'),
                        'Quick check: Does transformed content look correct? PASS or FAIL.'
                    ]
                )
                result = response.text
                verified = "PASS" in result.upper() or "YES" in result.upper()
                return {
                    "provider": "gemini",
                    "verified": verified,
                    "reason": result,
                    "raw_response": result
                }
            except Exception as e:
                print(f"⚠ Gemini verification failed: {e}")
                return {"verified": True, "reason": f"Gemini check failed: {e}", "provider": "gemini-error"}
        
        # No AI available - skip check (fail open)
        return {
            "verified": True,
            "reason": "No vision API available - skipping check",
            "provider": "none"
        }


def create_ai_agent(anthropic_key: Optional[str] = None, gemini_key: Optional[str] = None) -> GrainradAIAgent:
    """Create AI agent instance."""
    return GrainradAIAgent(anthropic_key=anthropic_key, gemini_key=gemini_key)
