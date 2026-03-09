"""
Block definitions and registry for workflow canvas.
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import json
import uuid


class BlockDefinition:
    """Definition of a block type."""
    
    def __init__(
        self,
        type: str,
        name: str,
        category: str,
        description: str,
        inputs: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]],
        icon: Optional[str] = None,
        color: Optional[str] = None
    ):
        self.type = type
        self.name = name
        self.category = category
        self.description = description
        self.inputs = inputs
        self.outputs = outputs
        self.icon = icon
        self.color = color


class BlockExecutor:
    """Executes blocks based on their type."""
    
    async def execute_block(self, block, context: Dict) -> Any:
        """Execute a block and return result."""
        block_type = block.type
        
        # Get input data from context
        input_data = self._get_block_inputs(block, context)
        
        # Execute based on block type
        if block_type == "input_http":
            return await self._execute_http_input(block, input_data)
        elif block_type == "resource_data":
            return await self._execute_data_input(block, input_data)
        elif block_type == "transform_json":
            return await self._execute_json_transform(block, input_data)
        elif block_type == "transform_text":
            return await self._execute_text_transform(block, input_data)
        elif block_type == "control_if":
            return await self._execute_if(block, input_data)
        elif block_type == "control_loop":
            return await self._execute_loop(block, input_data)
        elif block_type == "output_http":
            return await self._execute_http_output(block, input_data)
        elif block_type == "output_console":
            return await self._execute_console_output(block, input_data)
        elif block_type == "mcp_tool":
            return await self._execute_mcp_tool(block, input_data)
        elif block_type == "mcp_chain":
            return await self._execute_mcp_chain(block, input_data)
        elif block_type == "prompt_llm":
            return await self._execute_prompt_llm(block, input_data)
        elif block_type == "prompt_template":
            return await self._execute_prompt_template(block, input_data)
        elif block_type == "prompt_chain":
            return await self._execute_prompt_chain(block, input_data)
        elif block_type == "rag_ingest":
            return await self._execute_rag_ingest(block, input_data)
        elif block_type == "rag_search":
            return await self._execute_rag_search(block, input_data)
        elif block_type == "rag_subgraph":
            return await self._execute_rag_subgraph(block, input_data)
        elif block_type == "resource_file":
            return await self._execute_resource_file(block, input_data)
        elif block_type == "resource_database":
            return await self._execute_resource_database(block, input_data)
        elif block_type == "restriction_rate_limit":
            return await self._execute_rate_limit(block, input_data)
        elif block_type == "restriction_access_control":
            return await self._execute_access_control(block, input_data)
        elif block_type == "restriction_validation":
            return await self._execute_validation(block, input_data)
        elif block_type == "restriction_quota":
            return await self._execute_quota(block, input_data)
        elif block_type == "restriction_time_window":
            return await self._execute_time_window(block, input_data)
        elif block_type == "restriction_condition":
            return await self._execute_restriction_condition(block, input_data)
        else:
            # Default: pass through
            return input_data
    
    def _get_block_inputs(self, block, context: Dict) -> Any:
        """Get input data for a block from context."""
        # Check if block has direct input data
        if "input" in block.data:
            return block.data["input"]
        
        # Check connections for input
        for conn in block.connections:
            if conn.get("to") == block.id:
                from_block_id = conn.get("from")
                if from_block_id in context.get("results", {}):
                    return context["results"][from_block_id]
        
        # Fallback to workflow input
        return context.get("input", {})
    
    async def _execute_http_input(self, block, input_data: Any) -> Dict:
        """Execute HTTP input block."""
        import aiohttp
        
        url = block.data.get("url", "")
        method = block.data.get("method", "GET")
        headers = block.data.get("headers", {})
        body = block.data.get("body")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=body) as response:
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": await response.json() if response.content_type == "application/json" else await response.text()
                }
    
    async def _execute_data_input(self, block, input_data: Any) -> Any:
        """Execute data input block."""
        return block.data.get("value", input_data)
    
    async def _execute_json_transform(self, block, input_data: Any) -> Any:
        """Execute JSON transform block."""
        transform_type = block.data.get("transform", "parse")
        
        if transform_type == "parse":
            if isinstance(input_data, str):
                return json.loads(input_data)
            return input_data
        elif transform_type == "stringify":
            return json.dumps(input_data)
        elif transform_type == "get":
            path = block.data.get("path", "")
            if path:
                parts = path.split(".")
                result = input_data
                for part in parts:
                    if isinstance(result, dict):
                        result = result.get(part)
                    else:
                        return None
                return result
            return input_data
        else:
            return input_data
    
    async def _execute_text_transform(self, block, input_data: Any) -> str:
        """Execute text transform block."""
        transform_type = block.data.get("transform", "uppercase")
        text = str(input_data)
        
        if transform_type == "uppercase":
            return text.upper()
        elif transform_type == "lowercase":
            return text.lower()
        elif transform_type == "reverse":
            return text[::-1]
        elif transform_type == "replace":
            find = block.data.get("find", "")
            replace = block.data.get("replace", "")
            return text.replace(find, replace)
        else:
            return text
    
    async def _execute_if(self, block, input_data: Any) -> Any:
        """Execute if/else control block."""
        condition = block.data.get("condition", "")
        condition_value = self._evaluate_condition(condition, input_data)
        
        if condition_value:
            return block.data.get("true_value", input_data)
        else:
            return block.data.get("false_value", input_data)
    
    def _evaluate_condition(self, condition: str, data: Any) -> bool:
        """Evaluate a condition string."""
        # Simple condition evaluation
        # In production, use a proper expression evaluator
        try:
            # Replace data references
            if isinstance(data, dict):
                for key, value in data.items():
                    condition = condition.replace(f"${key}", str(value))
            
            # Evaluate as Python expression (simplified)
            return bool(eval(condition))
        except:
            return False
    
    async def _execute_loop(self, block, input_data: Any) -> List:
        """Execute loop control block."""
        items = input_data if isinstance(input_data, list) else [input_data]
        result = []
        
        for item in items:
            # Execute loop body (simplified)
            result.append(item)
        
        return result
    
    async def _execute_http_output(self, block, input_data: Any) -> Dict:
        """Execute HTTP output block."""
        # In a real implementation, this would send HTTP response
        return {
            "status": "sent",
            "data": input_data,
            "url": block.data.get("url", "")
        }
    
    async def _execute_console_output(self, block, input_data: Any) -> Any:
        """Execute console output block."""
        print(f"[Workflow Console] {input_data}")
        return input_data
    
    async def _execute_mcp_tool(self, block, input_data: Any) -> Any:
        """Execute MCP tool block."""
        from mcp_integration import MCPExecutor
        
        executor = MCPExecutor()
        tool_id = block.data.get("tool_id") or input_data.get("tool_id")
        parameters = block.data.get("parameters", {}) or input_data.get("parameters", {})
        
        if not tool_id:
            raise ValueError("MCP tool ID required")
        
        result = await executor.execute_tool(tool_id, parameters)
        return result
    
    async def _execute_mcp_chain(self, block, input_data: Any) -> Any:
        """Execute MCP tool chain block."""
        from mcp_integration import MCPExecutor
        
        executor = MCPExecutor()
        tools = block.data.get("tools", []) or input_data.get("tools", [])
        
        results = []
        for tool_config in tools:
            tool_id = tool_config.get("tool_id")
            parameters = tool_config.get("parameters", {})
            
            if tool_id:
                result = await executor.execute_tool(tool_id, parameters)
                results.append(result)
        
        return results
    
    async def _execute_rag_ingest(self, block, input_data: Any) -> Any:
        """Execute RAG ingest block."""
        from rag_graph import RAGGraph
        
        # Get or create RAG graph from context
        rag_graph = getattr(self, '_rag_graph', None)
        if not rag_graph:
            rag_graph = RAGGraph()
            setattr(self, '_rag_graph', rag_graph)
        
        document = block.data.get("document") or input_data.get("document") or str(input_data)
        metadata = block.data.get("metadata", {}) or input_data.get("metadata", {})
        
        node_id = rag_graph.ingest_document(
            document_id=str(uuid.uuid4()),
            content=document,
            metadata=metadata
        )
        
        return {"node_id": node_id, "status": "ingested"}
    
    async def _execute_rag_search(self, block, input_data: Any) -> Any:
        """Execute RAG search block."""
        from rag_graph import RAGGraph
        
        rag_graph = getattr(self, '_rag_graph', None)
        if not rag_graph:
            rag_graph = RAGGraph()
            setattr(self, '_rag_graph', rag_graph)
        
        query = block.data.get("query") or input_data.get("query") or str(input_data)
        node_type = block.data.get("node_type")
        limit = block.data.get("limit", 10)
        
        results = rag_graph.search_nodes(query, node_type, limit)
        
        return {
            "results": [node.to_dict() for node in results],
            "count": len(results)
        }
    
    async def _execute_rag_subgraph(self, block, input_data: Any) -> Any:
        """Execute RAG subgraph block."""
        from rag_graph import RAGGraph
        
        rag_graph = getattr(self, '_rag_graph', None)
        if not rag_graph:
            rag_graph = RAGGraph()
            setattr(self, '_rag_graph', rag_graph)
        
        node_id = block.data.get("node_id") or input_data.get("node_id")
        depth = block.data.get("depth", 2) or input_data.get("depth", 2)
        
        if not node_id:
            raise ValueError("Node ID required")
        
        subgraph = rag_graph.get_subgraph(node_id, depth)
        return subgraph
    
    async def _execute_prompt_llm(self, block, input_data: Any) -> Any:
        """Execute LLM prompt block."""
        from mcp_integration import MCPExecutor
        
        executor = MCPExecutor()
        prompt = block.data.get("prompt") or input_data.get("prompt") or str(input_data)
        context = block.data.get("context") or input_data.get("context", {})
        
        # Use MCP LLM tool
        result = await executor.execute_tool(
            "mcp_llm_complete",
            {
                "prompt": prompt,
                "model": block.data.get("model", "gpt-4"),
                "temperature": block.data.get("temperature", 0.7),
                "context": context
            }
        )
        
        return result.get("text", result)
    
    async def _execute_prompt_template(self, block, input_data: Any) -> str:
        """Execute prompt template block."""
        template = block.data.get("template") or input_data.get("template", "")
        variables = block.data.get("variables", {}) or input_data.get("variables", {})
        
        # Simple template replacement
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
            result = result.replace(f"${{{key}}}", str(value))
        
        return result
    
    async def _execute_prompt_chain(self, block, input_data: Any) -> List[Any]:
        """Execute prompt chain block."""
        prompts = block.data.get("prompts", []) or input_data.get("prompts", [])
        
        results = []
        for prompt_config in prompts:
            prompt = prompt_config.get("prompt", "")
            if prompt:
                # Execute each prompt
                result = await self._execute_prompt_llm(
                    type('Block', (), {'data': prompt_config})(),
                    {"prompt": prompt}
                )
                results.append(result)
        
        return results
    
    async def _execute_resource_file(self, block, input_data: Any) -> Any:
        """Execute file resource block."""
        from mcp_integration import MCPExecutor
        
        executor = MCPExecutor()
        path = block.data.get("path") or input_data.get("path")
        mode = block.data.get("mode", "read")  # read or write
        
        if not path:
            raise ValueError("File path required")
        
        if mode == "read":
            result = await executor.execute_tool("mcp_file_read", {"path": path})
            return result.get("content", result)
        else:
            content = block.data.get("content") or input_data.get("content", "")
            result = await executor.execute_tool("mcp_file_write", {"path": path, "content": content})
            return result
    
    async def _execute_resource_database(self, block, input_data: Any) -> Any:
        """Execute database resource block."""
        from mcp_integration import MCPExecutor
        
        executor = MCPExecutor()
        query = block.data.get("query") or input_data.get("query")
        database = block.data.get("database") or input_data.get("database", "default")
        
        if not query:
            raise ValueError("Database query required")
        
        result = await executor.execute_tool("mcp_db_query", {"query": query, "database": database})
        return result
    
    async def _execute_rate_limit(self, block, input_data: Any) -> Dict:
        """Execute rate limit restriction block."""
        from datetime import datetime, timedelta
        
        requests = block.data.get("requests") or input_data.get("requests", 0)
        window_seconds = block.data.get("window") or input_data.get("window", 60)
        
        # Simple in-memory rate limiter (in production, use Redis or similar)
        if not hasattr(self, '_rate_limits'):
            setattr(self, '_rate_limits', {})
        
        rate_limits = getattr(self, '_rate_limits')
        key = f"rate_limit_{block.id}"
        
        if key not in rate_limits:
            rate_limits[key] = {
                'count': 0,
                'window_start': datetime.now()
            }
        
        limit_data = rate_limits[key]
        now = datetime.now()
        
        # Reset if window expired
        if (now - limit_data['window_start']).total_seconds() > window_seconds:
            limit_data['count'] = 0
            limit_data['window_start'] = now
        
        # Check limit
        allowed = limit_data['count'] < requests
        if allowed:
            limit_data['count'] += 1
        
        remaining = max(0, requests - limit_data['count'])
        
        return {
            "allowed": allowed,
            "remaining": remaining,
            "count": limit_data['count'],
            "limit": requests
        }
    
    async def _execute_access_control(self, block, input_data: Any) -> Dict:
        """Execute access control restriction block."""
        user = block.data.get("user") or input_data.get("user", "")
        resource = block.data.get("resource") or input_data.get("resource", "")
        permission = block.data.get("permission") or input_data.get("permission", "read")
        
        # Simple access control (in production, use proper auth system)
        # Default: allow all (can be configured)
        allowed = block.data.get("default_allow", True)
        reason = "Access granted"
        
        # Check against rules if provided
        rules = block.data.get("rules", {})
        if rules:
            user_permissions = rules.get(user, {})
            resource_permissions = user_permissions.get(resource, [])
            allowed = permission in resource_permissions
            reason = "Access granted" if allowed else f"User {user} lacks {permission} permission for {resource}"
        
        return {
            "allowed": allowed,
            "reason": reason,
            "user": user,
            "resource": resource,
            "permission": permission
        }
    
    async def _execute_validation(self, block, input_data: Any) -> Dict:
        """Execute validation restriction block."""
        data = block.data.get("data") or input_data.get("data") or input_data
        rules = block.data.get("rules", {}) or input_data.get("rules", {})
        
        errors = []
        valid = True
        
        # Validate against rules
        if isinstance(rules, dict):
            # Type validation
            if "type" in rules:
                expected_type = rules["type"]
                if not isinstance(data, self._get_python_type(expected_type)):
                    errors.append(f"Expected type {expected_type}, got {type(data).__name__}")
                    valid = False
            
            # Required fields
            if "required" in rules and isinstance(data, dict):
                for field in rules["required"]:
                    if field not in data:
                        errors.append(f"Required field '{field}' is missing")
                        valid = False
            
            # Min/Max validation
            if "min" in rules:
                if isinstance(data, (int, float)) and data < rules["min"]:
                    errors.append(f"Value {data} is below minimum {rules['min']}")
                    valid = False
                elif isinstance(data, str) and len(data) < rules["min"]:
                    errors.append(f"String length {len(data)} is below minimum {rules['min']}")
                    valid = False
            
            if "max" in rules:
                if isinstance(data, (int, float)) and data > rules["max"]:
                    errors.append(f"Value {data} exceeds maximum {rules['max']}")
                    valid = False
                elif isinstance(data, str) and len(data) > rules["max"]:
                    errors.append(f"String length {len(data)} exceeds maximum {rules['max']}")
                    valid = False
        
        return {
            "valid": valid,
            "errors": errors,
            "data": data
        }
    
    def _get_python_type(self, type_name: str):
        """Convert type name string to Python type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "float": float,
            "boolean": bool,
            "array": list,
            "object": dict,
            "any": object
        }
        return type_map.get(type_name.lower(), object)
    
    async def _execute_quota(self, block, input_data: Any) -> Dict:
        """Execute quota restriction block."""
        resource = block.data.get("resource") or input_data.get("resource", "default")
        amount = block.data.get("amount") or input_data.get("amount", 0)
        
        # Simple quota tracker (in production, use persistent storage)
        if not hasattr(self, '_quotas'):
            setattr(self, '_quotas', {})
        
        quotas = getattr(self, '_quotas')
        
        if resource not in quotas:
            quotas[resource] = {
                'limit': block.data.get("limit", 1000),
                'used': 0
            }
        
        quota_data = quotas[resource]
        new_used = quota_data['used'] + amount
        within_quota = new_used <= quota_data['limit']
        
        if within_quota:
            quota_data['used'] = new_used
        
        remaining = max(0, quota_data['limit'] - quota_data['used'])
        
        return {
            "within_quota": within_quota,
            "remaining": remaining,
            "used": quota_data['used'],
            "limit": quota_data['limit'],
            "resource": resource
        }
    
    async def _execute_time_window(self, block, input_data: Any) -> Dict:
        """Execute time window restriction block."""
        from datetime import datetime
        
        start_time = block.data.get("start_time") or input_data.get("start_time", "00:00")
        end_time = block.data.get("end_time") or input_data.get("end_time", "23:59")
        
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        
        # Parse time strings (HH:MM format)
        try:
            start_hour, start_min = map(int, start_time.split(":"))
            end_hour, end_min = map(int, end_time.split(":"))
            
            current_hour, current_min = map(int, current_time_str.split(":"))
            
            # Convert to minutes for comparison
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            current_minutes = current_hour * 60 + current_min
            
            # Check if current time is within window
            if start_minutes <= end_minutes:
                # Normal case: start < end (e.g., 09:00 to 17:00)
                allowed = start_minutes <= current_minutes <= end_minutes
            else:
                # Overnight case: start > end (e.g., 22:00 to 06:00)
                allowed = current_minutes >= start_minutes or current_minutes <= end_minutes
            
        except (ValueError, AttributeError):
            allowed = True  # Default to allowed if parsing fails
        
        return {
            "allowed": allowed,
            "current_time": current_time_str,
            "start_time": start_time,
            "end_time": end_time
        }
    
    async def _execute_restriction_condition(self, block, input_data: Any) -> Dict:
        """Execute conditional restriction block."""
        condition = block.data.get("condition") or input_data.get("condition", True)
        action = block.data.get("action") or input_data.get("action", "block")
        
        # Evaluate condition
        if isinstance(condition, str):
            # Try to evaluate as boolean expression
            condition = condition.lower() in ("true", "1", "yes", "on")
        
        restricted = not bool(condition) if action == "block" else bool(condition)
        
        message = block.data.get("message", "")
        if not message:
            if restricted:
                message = "Access restricted by condition"
            else:
                message = "Access allowed"
        
        return {
            "restricted": restricted,
            "message": message,
            "condition": condition,
            "action": action
        }


class BlockRegistry:
    """Registry of available block types."""
    
    def __init__(self):
        self.blocks = self._initialize_blocks()
    
    def _initialize_blocks(self) -> Dict[str, BlockDefinition]:
        """Initialize all block definitions."""
        blocks = {}
        
        # ===== TOOLS =====
        # MCP tool execution blocks
        blocks["mcp_tool"] = BlockDefinition(
            type="mcp_tool",
            name="MCP Tool",
            category="tools",
            description="Execute an MCP tool",
            inputs=[{"name": "tool_id", "type": "string"}, {"name": "parameters", "type": "object"}],
            outputs=[{"name": "result", "type": "any"}],
            icon="🔧",
            color="#9E9E9E"
        )
        
        blocks["mcp_chain"] = BlockDefinition(
            type="mcp_chain",
            name="MCP Chain",
            category="tools",
            description="Chain multiple MCP tools",
            inputs=[{"name": "tools", "type": "array"}],
            outputs=[{"name": "results", "type": "array"}],
            icon="🔗",
            color="#607D8B"
        )
        
        blocks["input_http"] = BlockDefinition(
            type="input_http",
            name="HTTP Request",
            category="tools",
            description="Make an HTTP request",
            inputs=[],
            outputs=[{"name": "response", "type": "object"}],
            icon="🌐",
            color="#4CAF50"
        )
        
        blocks["output_http"] = BlockDefinition(
            type="output_http",
            name="HTTP Response",
            category="tools",
            description="Send HTTP response",
            inputs=[{"name": "data", "type": "any"}],
            outputs=[],
            icon="📤",
            color="#00BCD4"
        )
        
        # ===== PROMPTS =====
        # LLM and prompt-related blocks
        blocks["prompt_llm"] = BlockDefinition(
            type="prompt_llm",
            name="LLM Prompt",
            category="prompts",
            description="Send prompt to LLM",
            inputs=[{"name": "prompt", "type": "string"}, {"name": "context", "type": "any"}],
            outputs=[{"name": "response", "type": "string"}],
            icon="🤖",
            color="#9C27B0"
        )
        
        blocks["prompt_template"] = BlockDefinition(
            type="prompt_template",
            name="Prompt Template",
            category="prompts",
            description="Template prompt with variables",
            inputs=[{"name": "template", "type": "string"}, {"name": "variables", "type": "object"}],
            outputs=[{"name": "prompt", "type": "string"}],
            icon="📝",
            color="#E91E63"
        )
        
        blocks["prompt_chain"] = BlockDefinition(
            type="prompt_chain",
            name="Prompt Chain",
            category="prompts",
            description="Chain multiple prompts",
            inputs=[{"name": "prompts", "type": "array"}],
            outputs=[{"name": "responses", "type": "array"}],
            icon="🔗",
            color="#F44336"
        )
        
        # ===== RESOURCES =====
        # Data sources, RAG, and resource blocks
        blocks["resource_data"] = BlockDefinition(
            type="resource_data",
            name="Data Resource",
            category="resources",
            description="Input data value",
            inputs=[],
            outputs=[{"name": "data", "type": "any"}],
            icon="📥",
            color="#2196F3"
        )
        
        blocks["rag_ingest"] = BlockDefinition(
            type="rag_ingest",
            name="RAG Ingest",
            category="resources",
            description="Ingest document into RAG graph",
            inputs=[{"name": "document", "type": "string"}, {"name": "metadata", "type": "object"}],
            outputs=[{"name": "node_id", "type": "string"}],
            icon="📚",
            color="#3F51B5"
        )
        
        blocks["rag_search"] = BlockDefinition(
            type="rag_search",
            name="RAG Search",
            category="resources",
            description="Search RAG graph",
            inputs=[{"name": "query", "type": "string"}],
            outputs=[{"name": "results", "type": "array"}],
            icon="🔍",
            color="#2196F3"
        )
        
        blocks["rag_subgraph"] = BlockDefinition(
            type="rag_subgraph",
            name="RAG Subgraph",
            category="resources",
            description="Get subgraph from node",
            inputs=[{"name": "node_id", "type": "string"}, {"name": "depth", "type": "number"}],
            outputs=[{"name": "subgraph", "type": "object"}],
            icon="🕸️",
            color="#00BCD4"
        )
        
        blocks["resource_file"] = BlockDefinition(
            type="resource_file",
            name="File Resource",
            category="resources",
            description="Read/write file resource",
            inputs=[{"name": "path", "type": "string"}],
            outputs=[{"name": "content", "type": "string"}],
            icon="📄",
            color="#FF9800"
        )
        
        blocks["resource_database"] = BlockDefinition(
            type="resource_database",
            name="Database Resource",
            category="resources",
            description="Query database resource",
            inputs=[{"name": "query", "type": "string"}],
            outputs=[{"name": "results", "type": "array"}],
            icon="🗄️",
            color="#795548"
        )
        
        # ===== TRANSFORM =====
        # Data transformation blocks
        blocks["transform_json"] = BlockDefinition(
            type="transform_json",
            name="JSON Transform",
            category="transform",
            description="Transform JSON data",
            inputs=[{"name": "data", "type": "any"}],
            outputs=[{"name": "result", "type": "any"}],
            icon="🔄",
            color="#FF9800"
        )
        
        blocks["transform_text"] = BlockDefinition(
            type="transform_text",
            name="Text Transform",
            category="transform",
            description="Transform text data",
            inputs=[{"name": "text", "type": "string"}],
            outputs=[{"name": "result", "type": "string"}],
            icon="✏️",
            color="#9C27B0"
        )
        
        # ===== CONTROL =====
        # Flow control blocks
        blocks["control_if"] = BlockDefinition(
            type="control_if",
            name="If/Else",
            category="control",
            description="Conditional logic",
            inputs=[{"name": "condition", "type": "boolean"}],
            outputs=[{"name": "result", "type": "any"}],
            icon="🔀",
            color="#F44336"
        )
        
        blocks["control_loop"] = BlockDefinition(
            type="control_loop",
            name="Loop",
            category="control",
            description="Loop through items",
            inputs=[{"name": "items", "type": "array"}],
            outputs=[{"name": "result", "type": "array"}],
            icon="🔁",
            color="#E91E63"
        )
        
        # ===== OUTPUT =====
        blocks["output_console"] = BlockDefinition(
            type="output_console",
            name="Console Output",
            category="output",
            description="Output to console",
            inputs=[{"name": "data", "type": "any"}],
            outputs=[],
            icon="💻",
            color="#795548"
        )
        
        # ===== RESTRICTIONS =====
        # Access control and restriction blocks
        blocks["restriction_rate_limit"] = BlockDefinition(
            type="restriction_rate_limit",
            name="Rate Limit",
            category="restrictions",
            description="Enforce rate limiting",
            inputs=[{"name": "requests", "type": "number"}, {"name": "window", "type": "number"}],
            outputs=[{"name": "allowed", "type": "boolean"}, {"name": "remaining", "type": "number"}],
            icon="⏱️",
            color="#FF5722"
        )
        
        blocks["restriction_access_control"] = BlockDefinition(
            type="restriction_access_control",
            name="Access Control",
            category="restrictions",
            description="Check access permissions",
            inputs=[{"name": "user", "type": "string"}, {"name": "resource", "type": "string"}, {"name": "permission", "type": "string"}],
            outputs=[{"name": "allowed", "type": "boolean"}, {"name": "reason", "type": "string"}],
            icon="🔒",
            color="#D32F2F"
        )
        
        blocks["restriction_validation"] = BlockDefinition(
            type="restriction_validation",
            name="Validation",
            category="restrictions",
            description="Validate data against rules",
            inputs=[{"name": "data", "type": "any"}, {"name": "rules", "type": "object"}],
            outputs=[{"name": "valid", "type": "boolean"}, {"name": "errors", "type": "array"}],
            icon="✅",
            color="#388E3C"
        )
        
        blocks["restriction_quota"] = BlockDefinition(
            type="restriction_quota",
            name="Quota",
            category="restrictions",
            description="Check and enforce quotas",
            inputs=[{"name": "resource", "type": "string"}, {"name": "amount", "type": "number"}],
            outputs=[{"name": "within_quota", "type": "boolean"}, {"name": "remaining", "type": "number"}],
            icon="📊",
            color="#F57C00"
        )
        
        blocks["restriction_time_window"] = BlockDefinition(
            type="restriction_time_window",
            name="Time Window",
            category="restrictions",
            description="Restrict execution to time window",
            inputs=[{"name": "start_time", "type": "string"}, {"name": "end_time", "type": "string"}],
            outputs=[{"name": "allowed", "type": "boolean"}, {"name": "current_time", "type": "string"}],
            icon="🕐",
            color="#7B1FA2"
        )
        
        blocks["restriction_condition"] = BlockDefinition(
            type="restriction_condition",
            name="Conditional Restriction",
            category="restrictions",
            description="Apply restriction based on condition",
            inputs=[{"name": "condition", "type": "boolean"}, {"name": "action", "type": "string"}],
            outputs=[{"name": "restricted", "type": "boolean"}, {"name": "message", "type": "string"}],
            icon="🚫",
            color="#C62828"
        )
        
        return blocks
    
    def get_all_blocks(self) -> List[Dict]:
        """Get all block definitions as dictionaries."""
        return [
            {
                "type": block.type,
                "name": block.name,
                "category": block.category,
                "description": block.description,
                "inputs": block.inputs,
                "outputs": block.outputs,
                "icon": block.icon,
                "color": block.color
            }
            for block in self.blocks.values()
        ]
    
    def get_categories(self) -> List[str]:
        """Get all block categories."""
        categories = list(set(block.category for block in self.blocks.values()))
        # Ensure order: tools, prompts, resources, transform, control, restrictions, output
        ordered = ['tools', 'prompts', 'resources', 'transform', 'control', 'restrictions', 'output']
        return [c for c in ordered if c in categories] + [c for c in categories if c not in ordered]
    
    def get_block_info(self, block_type: str) -> Optional[Dict]:
        """Get information about a specific block type."""
        block = self.blocks.get(block_type)
        if block:
            return {
                "type": block.type,
                "name": block.name,
                "category": block.category,
                "description": block.description,
                "inputs": block.inputs,
                "outputs": block.outputs,
                "icon": block.icon,
                "color": block.color
            }
        return None
