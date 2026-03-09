"""
AI Gateway integration for chat interface.
Handles AI-powered command processing and workflow assistance.
"""

from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime


class AIGateway:
    """
    AI Gateway for processing chat commands and workflow assistance.
    Supports multiple AI providers (Claude, OpenAI, etc.)
    """
    
    def __init__(self, provider: str = "anthropic", api_key: Optional[str] = None):
        """
        Initialize AI Gateway.
        
        Args:
            provider: AI provider ('anthropic', 'openai', 'local')
            api_key: API key (or use environment variable)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.conversation_history: List[Dict] = []
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        if self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None
    
    async def process_command(
        self,
        command: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a chat command using AI.
        
        Args:
            command: User command
            context: Workflow context (nodes, connections, etc.)
            
        Returns:
            Response with action and message
        """
        # Build prompt with context
        system_prompt = self._build_system_prompt(context)
        user_prompt = self._build_user_prompt(command, context)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": command,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process with AI
        try:
            response = await self._call_ai(system_prompt, user_prompt)
            
            # Parse response
            action = self._parse_action(response, context)
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "message": response,
                "action": action,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing command: {str(e)}",
                "action": None,
                "error": str(e)
            }
    
    def _build_system_prompt(self, context: Optional[Dict]) -> str:
        """Build system prompt for AI."""
        prompt = """You are an AI assistant for a workflow canvas application. 
You help users build and manage workflows using natural language commands.

Available block types:
- Tools: input_http, output_http, mcp_tool, mcp_chain
- Prompts: prompt_llm, prompt_template, prompt_chain
- Resources: resource_data, rag_ingest, rag_search, rag_subgraph, resource_file, resource_database
- Transform: transform_json, transform_text
- Control: control_if, control_loop
- Restrictions: restriction_rate_limit, restriction_access_control, restriction_validation, etc.
- Output: output_console

When users ask to:
- "Add [block type] node" → Return action: {"type": "add_node", "block_type": "[type]", "position": {"x": 100, "y": 100}}
- "Clear canvas" → Return action: {"type": "clear_canvas"}
- "Connect [node1] to [node2]" → Return action: {"type": "connect", "from": "[id]", "to": "[id]"}
- "Save workflow" → Return action: {"type": "save_workflow"}
- "Execute workflow" → Return action: {"type": "execute_workflow"}
- "Show blocks" → Return action: {"type": "list_nodes"}

Response format: Start with the action or a one-line summary of what you're doing (e.g. \"Action: add_node, block_type: mcp_tool\"), then add a brief friendly explanation. This helps the system parse the action quickly and show progress.
Always respond in a helpful, conversational way. If you can't understand a command, suggest alternatives."""
        
        if context:
            nodes = context.get('nodes', [])
            if nodes:
                prompt += f"\n\nCurrent workflow has {len(nodes)} nodes: {[n.get('type') for n in nodes]}"
        
        return prompt
    
    def _build_user_prompt(self, command: str, context: Optional[Dict]) -> str:
        """Build user prompt."""
        prompt = f"User command: {command}"
        
        if context:
            prompt += f"\n\nWorkflow context: {json.dumps(context, indent=2)}"
        
        return prompt
    
    async def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call AI provider.
        
        For now, uses a simple rule-based system.
        In production, would call actual AI API.
        """
        # Simple rule-based processing (can be replaced with actual AI call)
        command = user_prompt.lower()
        
        if "add" in command and "node" in command:
            # Extract block type
            block_type = self._extract_block_type(command)
            return f"I'll add a {block_type} node to your canvas. Action: add_node"
        
        elif "clear" in command or "reset" in command:
            return "I'll clear the canvas for you. Action: clear_canvas"
        
        elif "show" in command and "block" in command:
            return "Here are the current blocks on your canvas. Action: list_nodes"
        
        elif "connect" in command:
            return "I'll help you connect those nodes. Please specify which nodes to connect. Action: connect"
        
        elif "save" in command:
            return "Saving your workflow now. Action: save_workflow"
        
        elif "execute" in command or "run" in command:
            return "Executing your workflow. Action: execute_workflow"
        
        elif "help" in command:
            return """I can help you with:
• Adding nodes: "Add [block type] node"
• Clearing canvas: "Clear canvas"
• Showing blocks: "Show blocks"
• Connecting nodes: "Connect node A to node B"
• Saving: "Save workflow"
• Executing: "Execute workflow"
• Exporting: "Export to N8N"
• Importing: "Import N8N workflow\""""
        
        else:
            return f"I understand you want to: {command}. Could you be more specific? Try 'help' for available commands."
    
    def _extract_block_type(self, command: str) -> str:
        """Extract block type from command."""
        block_keywords = {
            'http': 'input_http',
            'http request': 'input_http',
            'mcp': 'mcp_tool',
            'mcp tool': 'mcp_tool',
            'rag': 'rag_ingest',
            'rag ingest': 'rag_ingest',
            'prompt': 'prompt_llm',
            'llm': 'prompt_llm',
            'data': 'resource_data',
            'resource': 'resource_data',
            'file': 'resource_file',
            'database': 'resource_database',
            'transform': 'transform_json',
            'if': 'control_if',
            'loop': 'control_loop'
        }
        
        for keyword, block_type in block_keywords.items():
            if keyword in command.lower():
                return block_type
        
        return 'resource_data'  # Default
    
    def _parse_action(self, response: str, context: Optional[Dict]) -> Optional[Dict]:
        """Parse action from AI response."""
        # Extract action from response
        if "Action: add_node" in response:
            block_type = self._extract_block_type(response)
            return {
                "type": "add_node",
                "block_type": block_type,
                "position": {"x": 100, "y": 100}
            }
        elif "Action: clear_canvas" in response:
            return {"type": "clear_canvas"}
        elif "Action: list_nodes" in response:
            return {"type": "list_nodes"}
        elif "Action: connect" in response:
            return {"type": "connect"}
        elif "Action: save_workflow" in response:
            return {"type": "save_workflow"}
        elif "Action: execute_workflow" in response:
            return {"type": "execute_workflow"}
        
        return None
    
    async def call_claude_api(self, messages: List[Dict]) -> str:
        """
        Call Claude API (when API key is available).
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            AI response text
        """
        if not self.api_key:
            # Fallback to rule-based
            return await self._call_ai("", messages[-1].get('content', ''))
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 1024,
                        "messages": messages
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('content', [{}])[0].get('text', '')
                else:
                    return f"API Error: {response.status_code}"
        except ImportError:
            return "httpx not installed. Install with: pip install httpx"
        except Exception as e:
            return f"Error calling Claude API: {str(e)}"
