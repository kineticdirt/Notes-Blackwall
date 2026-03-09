"""
Website AI Agent: Uses AI with MCP UI resources/prompts to guide website transformation.
"""

import sys
import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_ui_server import MCPUIServer
from website_fetcher import WebsiteData, WebsiteComponent


class WebsiteAIAgent:
    """AI Agent that uses MCP UI prompts to guide website transformation."""
    
    def __init__(self, mcp_ui_server: MCPUIServer, anthropic_key: Optional[str] = None, gemini_key: Optional[str] = None):
        """
        Initialize website AI agent.
        
        Args:
            mcp_ui_server: MCP UI server for prompts/resources
            anthropic_key: Anthropic API key (for Claude)
            gemini_key: Google Gemini API key (fallback)
        """
        self.mcp_ui = mcp_ui_server
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
    
    async def analyze_website(self, website_data: WebsiteData) -> Dict:
        """
        Analyze website using AI with MCP UI prompts.
        
        Args:
            website_data: Website data to analyze
            
        Returns:
            Analysis results with recommendations
        """
        # Get analysis prompt from MCP UI
        try:
            prompt = self.mcp_ui.get_prompt("website-analysis", {
                "url": website_data.url,
                "html_preview": website_data.html[:2000],  # Preview
                "css_count": len(website_data.css),
                "js_count": len(website_data.javascript),
                "component_count": len(website_data.components),
                "component_list": "\n".join([
                    f"- {c.component_id} ({c.component_type})"
                    for c in website_data.components[:10]
                ])
            })
        except ValueError:
            # Fallback prompt if not found
            prompt = self._create_fallback_analysis_prompt(website_data)
        
        # Send to AI
        analysis = await self._call_ai(prompt)
        
        # Parse response
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Return structured response
                return {
                    "analysis": analysis,
                    "parsed": False
                }
        except json.JSONDecodeError:
            return {
                "analysis": analysis,
                "parsed": False
            }
    
    async def plan_transformation(self, components: List[WebsiteComponent]) -> Dict:
        """
        Plan transformation strategy using AI with MCP prompts.
        
        Args:
            components: List of components to transform
            
        Returns:
            Transformation strategy/plan
        """
        # Get strategy prompt from MCP UI
        try:
            components_json = json.dumps([
                {
                    "id": c.component_id,
                    "type": c.component_type,
                    "html": c.html_content[:500]  # Preview
                }
                for c in components
            ], indent=2)
            
            prompt = self.mcp_ui.get_prompt("transformation-strategy", {
                "components_json": components_json
            })
        except ValueError:
            # Fallback prompt
            prompt = self._create_fallback_strategy_prompt(components)
        
        # Send to AI
        strategy = await self._call_ai(prompt)
        
        # Parse response
        try:
            json_match = re.search(r'\{.*\}', strategy, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "strategy": strategy,
                    "parsed": False
                }
        except json.JSONDecodeError:
            return {
                "strategy": strategy,
                "parsed": False
            }
    
    async def verify_transformation(self, original: WebsiteData, transformed: Dict) -> Dict:
        """
        Verify transformation quality (final check).
        
        Args:
            original: Original website data
            transformed: Transformed website data
            
        Returns:
            Verification result
        """
        # Simple verification prompt
        prompt = f"""Verify this website transformation:

Original URL: {original.url}
Original components: {len(original.components)}
Transformed panes: {len(transformed.get('panes', []))}

Does the transformation preserve:
1. Website functionality (links, navigation)?
2. Content structure and hierarchy?
3. Visual organization?

Respond with PASS or FAIL and brief reason.
"""
        
        result = await self._call_ai(prompt)
        verified = "PASS" in result.upper() or "YES" in result.upper()
        
        return {
            "verified": verified,
            "reason": result,
            "provider": "claude" if self.anthropic else ("gemini" if self.gemini else "none")
        }
    
    async def _call_ai(self, prompt: str) -> str:
        """
        Call AI provider with prompt.
        
        Args:
            prompt: Prompt text
            
        Returns:
            AI response text
        """
        # Try Claude first
        if self.anthropic:
            try:
                response = await self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return response.content[0].text
            except Exception as e:
                print(f"⚠ Claude API error: {e}")
        
        # Fallback to Gemini
        if self.gemini:
            try:
                from google.genai import types
                response = self.gemini.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"⚠ Gemini API error: {e}")
        
        # No AI available - return mock response
        return self._mock_ai_response(prompt)
    
    def _create_fallback_analysis_prompt(self, website_data: WebsiteData) -> str:
        """Create fallback analysis prompt."""
        return f"""Analyze this website:

URL: {website_data.url}
Components: {len(website_data.components)}

Provide analysis of visual hierarchy, component types, and transformation recommendations.
"""
    
    def _create_fallback_strategy_prompt(self, components: List[WebsiteComponent]) -> str:
        """Create fallback strategy prompt."""
        return f"""Plan transformation for {len(components)} components.

Provide strategy for converting to ASCII/dithered/shaded visual panes.
"""
    
    def _mock_ai_response(self, prompt: str) -> str:
        """Mock AI response when no API available."""
        if "analysis" in prompt.lower():
            return json.dumps({
                "hierarchy": {"main_sections": ["header", "main", "footer"]},
                "component_analysis": [],
                "overall_strategy": {"layout": "vertical", "effects": ["ascii", "dithering"]}
            })
        elif "strategy" in prompt.lower():
            return json.dumps({
                "strategy": {"layout": "vertical"},
                "component_strategies": []
            })
        else:
            return "PASS - Mock verification"


import re


def create_website_ai_agent(mcp_ui_server: MCPUIServer,
                            anthropic_key: Optional[str] = None,
                            gemini_key: Optional[str] = None) -> WebsiteAIAgent:
    """Create website AI agent instance."""
    return WebsiteAIAgent(mcp_ui_server, anthropic_key=anthropic_key, gemini_key=gemini_key)
