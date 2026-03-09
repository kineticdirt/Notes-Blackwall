"""
N8N workflow format converter.
Converts between our workflow format and N8N format for compatibility.
"""

from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime


class N8NConverter:
    """Converter between our workflow format and N8N format."""
    
    # Mapping from our block types to N8N node types
    BLOCK_TO_N8N = {
        'input_http': 'n8n-nodes-base.httpRequest',
        'output_http': 'n8n-nodes-base.respondToWebhook',
        'mcp_tool': 'n8n-nodes-base.code',
        'mcp_chain': 'n8n-nodes-base.code',
        'prompt_llm': 'n8n-nodes-base.httpRequest',
        'prompt_template': 'n8n-nodes-base.function',
        'prompt_chain': 'n8n-nodes-base.code',
        'resource_data': 'n8n-nodes-base.set',
        'rag_ingest': 'n8n-nodes-base.code',
        'rag_search': 'n8n-nodes-base.code',
        'rag_subgraph': 'n8n-nodes-base.code',
        'resource_file': 'n8n-nodes-base.readBinaryFile',
        'resource_database': 'n8n-nodes-base.postgres',
        'transform_json': 'n8n-nodes-base.function',
        'transform_text': 'n8n-nodes-base.function',
        'control_if': 'n8n-nodes-base.if',
        'control_loop': 'n8n-nodes-base.splitInBatches',
        'restriction_rate_limit': 'n8n-nodes-base.function',
        'restriction_access_control': 'n8n-nodes-base.function',
        'restriction_validation': 'n8n-nodes-base.function',
        'restriction_quota': 'n8n-nodes-base.function',
        'restriction_time_window': 'n8n-nodes-base.function',
        'restriction_condition': 'n8n-nodes-base.if',
        'output_console': 'n8n-nodes-base.noOp'
    }
    
    # Reverse mapping
    N8N_TO_BLOCK = {v: k for k, v in BLOCK_TO_N8N.items()}
    
    def to_n8n(self, workflow: Dict) -> Dict:
        """
        Convert our workflow format to N8N format.
        
        Args:
            workflow: Our workflow format
            
        Returns:
            N8N workflow format
        """
        nodes = []
        connections = {}
        
        # Convert blocks to N8N nodes
        node_id_map = {}  # Map our block IDs to N8N node IDs
        for block in workflow.get('blocks', []):
            n8n_node = self._block_to_n8n_node(block)
            nodes.append(n8n_node)
            node_id_map[block.get('id')] = n8n_node['id']
        
        # Build connections
        for conn in workflow.get('connections', []):
            from_block_id = conn.get('from')
            to_block_id = conn.get('to')
            
            from_n8n_id = node_id_map.get(from_block_id)
            to_n8n_id = node_id_map.get(to_block_id)
            
            if from_n8n_id and to_n8n_id:
                if from_n8n_id not in connections:
                    connections[from_n8n_id] = {}
                
                input_type = 'main'
                if input_type not in connections[from_n8n_id]:
                    connections[from_n8n_id][input_type] = []
                
                # Ensure we have at least one output array
                if len(connections[from_n8n_id][input_type]) == 0:
                    connections[from_n8n_id][input_type].append([])
                
                # Add connection
                connections[from_n8n_id][input_type][0].append({
                    'node': to_n8n_id,
                    'type': input_type,
                    'index': 0
                })
        
        return {
            'name': workflow.get('name', 'Untitled Workflow'),
            'nodes': nodes,
            'connections': connections,
            'pinData': {},
            'settings': {
                'executionOrder': 'v1'
            },
            'staticData': None,
            'tags': [],
            'triggerCount': 0,
            'updatedAt': datetime.now().isoformat(),
            'versionId': str(uuid.uuid4())
        }
    
    def from_n8n(self, n8n_workflow: Dict) -> Dict:
        """
        Convert N8N format to our workflow format.
        
        Args:
            n8n_workflow: N8N workflow format
            
        Returns:
            Our workflow format
        """
        blocks = []
        connections = []
        
        # Convert N8N nodes to blocks
        node_id_map = {}  # Map N8N node IDs to our block IDs
        
        for n8n_node in n8n_workflow.get('nodes', []):
            block = self._n8n_node_to_block(n8n_node)
            if block:
                blocks.append(block)
                node_id_map[n8n_node['id']] = block['id']
        
        # Convert connections
        n8n_connections = n8n_workflow.get('connections', {})
        for from_node_id, connection_data in n8n_connections.items():
            from_block_id = node_id_map.get(from_node_id)
            if not from_block_id:
                continue
            
            for input_type, outputs in connection_data.items():
                for output_index, targets in enumerate(outputs):
                    if isinstance(targets, list):
                        for target in targets:
                            if isinstance(target, dict):
                                to_node_id = target.get('node')
                            else:
                                to_node_id = target
                            
                            to_block_id = node_id_map.get(to_node_id)
                            if to_block_id:
                                connections.append({
                                    'from': from_block_id,
                                    'to': to_block_id,
                                    'fromPort': f'output_{output_index}',
                                    'toPort': 'input_0'
                                })
        
        # Add connections to blocks
        for block in blocks:
            block['connections'] = [
                conn for conn in connections
                if conn.get('from') == block['id'] or conn.get('to') == block['id']
            ]
        
        return {
            'name': n8n_workflow.get('name', 'Untitled Workflow'),
            'description': f"Imported from N8N",
            'blocks': blocks,
            'connections': connections
        }
    
    def _block_to_n8n_node(self, block: Dict) -> Dict:
        """Convert a block to N8N node format."""
        block_type = block.get('type', '')
        n8n_type = self.BLOCK_TO_N8N.get(block_type, 'n8n-nodes-base.code')
        
        position = block.get('position', {})
        
        node = {
            'parameters': self._convert_block_data(block),
            'id': self._get_node_id(block),
            'name': block.get('type', 'Node'),
            'type': n8n_type,
            'typeVersion': 1,
            'position': [
                position.get('x', 0),
                position.get('y', 0)
            ],
            'disabled': False,
            'notes': '',
            'notesInFlow': False
        }
        
        return node
    
    def _n8n_node_to_block(self, n8n_node: Dict) -> Optional[Dict]:
        """Convert N8N node to our block format."""
        n8n_type = n8n_node.get('type', '')
        block_type = self.N8N_TO_BLOCK.get(n8n_type)
        
        if not block_type:
            # Try to infer from node name or use code node
            block_type = 'mcp_tool'
        
        position = n8n_node.get('position', [0, 0])
        
        return {
            'id': n8n_node.get('id', str(uuid.uuid4())),
            'type': block_type,
            'position': {
                'x': position[0] if isinstance(position, list) else position.get('x', 0),
                'y': position[1] if isinstance(position, list) else position.get('y', 0)
            },
            'data': self._convert_n8n_parameters(n8n_node.get('parameters', {}))
        }
    
    def _convert_block_data(self, block: Dict) -> Dict:
        """Convert block data to N8N parameters."""
        data = block.get('data', {})
        block_type = block.get('type', '')
        
        # Convert based on block type
        if block_type == 'input_http':
            return {
                'method': data.get('method', 'GET'),
                'url': data.get('url', ''),
                'options': {}
            }
        elif block_type == 'mcp_tool':
            return {
                'jsCode': f"// MCP Tool: {data.get('tool_id', '')}\nreturn $input.all();"
            }
        elif block_type == 'prompt_llm':
            return {
                'method': 'POST',
                'url': data.get('api_url', 'https://api.anthropic.com/v1/messages'),
                'bodyParameters': {
                    'model': data.get('model', 'claude-3-5-sonnet-20241022'),
                    'messages': [{'role': 'user', 'content': data.get('prompt', '')}]
                }
            }
        else:
            return data
    
    def _convert_n8n_parameters(self, parameters: Dict) -> Dict:
        """Convert N8N parameters to block data."""
        return parameters
    
    def _get_node_id(self, block: Dict) -> str:
        """Get or generate node ID."""
        return block.get('id', str(uuid.uuid4()))
