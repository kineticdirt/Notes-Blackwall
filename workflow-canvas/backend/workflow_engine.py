"""
Workflow execution engine.
Executes workflows defined by blocks and connections.
"""

from typing import Dict, List, Any, Optional, AsyncIterator
import asyncio
from datetime import datetime
from blocks import BlockRegistry, BlockExecutor
from streaming import StreamManager
from execution_scheduler import ExecutionScheduler, ExecutionMode


class WorkflowEngine:
    """
    Executes workflows by running blocks in order based on connections.
    """
    
    def __init__(self):
        self.block_registry = BlockRegistry()
        self.executor = BlockExecutor()
        self.stream_manager = StreamManager()
        self.scheduler = ExecutionScheduler()
    
    async def execute_workflow(self, workflow, input_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a workflow synchronously.
        
        Args:
            workflow: Workflow object with blocks and connections
            input_data: Optional input data for the workflow
            
        Returns:
            Final execution result
        """
        # Build execution graph
        execution_order = self._build_execution_order(workflow.blocks, workflow.blocks)
        
        # Execute blocks in order
        context = {"input": input_data or {}, "results": {}}
        
        for block_ids in execution_order:
            # Execute blocks in parallel if no dependencies
            tasks = []
            for block_id in block_ids:
                block = self._find_block(workflow.blocks, block_id)
                if block:
                    tasks.append(self._execute_block(block, context))
            
            if tasks:
                await asyncio.gather(*tasks)
        
        return {
            "output": context.get("output"),
            "results": context["results"],
            "executed_at": datetime.now().isoformat()
        }
    
    async def execute_workflow_stream(
        self, 
        workflow, 
        input_data: Optional[Dict] = None,
        stream_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a workflow with streaming output.
        
        Args:
            workflow: Workflow object
            input_data: Optional input data
            stream_id: Stream ID for tracking
            
        Yields:
            Execution events as dictionaries
        """
        # Build execution graph
        execution_order = self._build_execution_order(workflow.blocks, workflow.blocks)
        
        # Execute blocks in order
        context = {"input": input_data or {}, "results": {}}
        
        yield {
            "type": "workflow_start",
            "workflow_id": workflow.id,
            "block_count": len(workflow.blocks),
            "timestamp": datetime.now().isoformat()
        }
        
        for block_ids in execution_order:
            # Get execution mode from workflow or block data
            execution_mode = ExecutionMode.SEQUENTIAL
            stagger_delay = 0.1
            
            # Execute blocks based on mode
            blocks_to_execute = [
                self._find_block(workflow.blocks, block_id)
                for block_id in block_ids
                if self._find_block(workflow.blocks, block_id)
            ]
            
            if execution_mode == ExecutionMode.PARALLEL:
                # Execute in parallel
                tasks = []
                for block in blocks_to_execute:
                    yield {
                        "type": "block_start",
                        "block_id": block.id,
                        "block_type": block.type,
                        "timestamp": datetime.now().isoformat()
                    }
                    tasks.append(self._execute_block_stream(block, context, stream_id))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, dict):
                        yield result
            else:
                # Execute sequentially or staggered
                for i, block in enumerate(blocks_to_execute):
                    if execution_mode == ExecutionMode.STAGGERED and i > 0:
                        await asyncio.sleep(stagger_delay)
                    
                    yield {
                        "type": "block_start",
                        "block_id": block.id,
                        "block_type": block.type,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    result = await self._execute_block_stream(block, context, stream_id)
                    yield result
        
        yield {
            "type": "workflow_complete",
            "workflow_id": workflow.id,
            "output": context.get("output"),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_block(self, block, context: Dict) -> Any:
        """Execute a single block."""
        try:
            result = await self.executor.execute_block(block, context)
            context["results"][block.id] = result
            
            # Update context output if this is an output block
            if block.type.startswith("output_"):
                context["output"] = result
            
            return result
        except Exception as e:
            context["results"][block.id] = {"error": str(e)}
            raise
    
    async def _execute_block_stream(
        self, 
        block, 
        context: Dict,
        stream_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a block and return streaming event."""
        try:
            result = await self.executor.execute_block(block, context)
            context["results"][block.id] = result
            
            # Update context output if this is an output block
            if block.type.startswith("output_"):
                context["output"] = result
            
            return {
                "type": "block_complete",
                "block_id": block.id,
                "block_type": block.type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "type": "block_error",
                "block_id": block.id,
                "block_type": block.type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_execution_order(
        self, 
        blocks: List, 
        all_blocks: List
    ) -> List[List[str]]:
        """
        Build execution order based on block connections.
        Returns list of lists, where each inner list contains blocks
        that can execute in parallel.
        """
        # Build dependency graph
        dependencies = {}
        block_ids = {block.id for block in blocks}
        
        for block in blocks:
            dependencies[block.id] = set()
            for conn in block.connections:
                if conn.get("from") in block_ids:
                    dependencies[block.id].add(conn["from"])
        
        # Topological sort
        execution_order = []
        executed = set()
        
        while len(executed) < len(block_ids):
            # Find blocks with no remaining dependencies
            ready = [
                block_id for block_id in block_ids
                if block_id not in executed and
                dependencies[block_id].issubset(executed)
            ]
            
            if not ready:
                # Circular dependency or error
                remaining = block_ids - executed
                ready = list(remaining)  # Force execution
            
            execution_order.append(ready)
            executed.update(ready)
        
        return execution_order
    
    def _find_block(self, blocks: List, block_id: str):
        """Find a block by ID."""
        for block in blocks:
            if block.id == block_id:
                return block
        return None
