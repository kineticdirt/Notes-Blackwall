"""
Execution scheduler for staggering workflow execution.
Allows sequential, parallel, and staggered execution of blocks.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio
from datetime import datetime


class ExecutionMode(Enum):
    """Execution modes for workflow blocks."""
    SEQUENTIAL = "sequential"  # Execute one after another
    PARALLEL = "parallel"      # Execute all at once
    STAGGERED = "staggered"    # Execute with delays
    CONDITIONAL = "conditional" # Execute based on conditions


class ExecutionScheduler:
    """
    Schedules and staggers workflow block execution.
    """
    
    def __init__(self):
        self.execution_history: List[Dict] = []
    
    async def execute_blocks(
        self,
        blocks: List[Any],
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        delay: float = 0.0,
        stagger_delay: float = 0.1
    ) -> List[Any]:
        """
        Execute blocks with specified scheduling mode.
        
        Args:
            blocks: List of blocks to execute
            mode: Execution mode
            delay: Initial delay before execution
            stagger_delay: Delay between staggered executions
            
        Returns:
            List of execution results
        """
        if delay > 0:
            await asyncio.sleep(delay)
        
        if mode == ExecutionMode.SEQUENTIAL:
            return await self._execute_sequential(blocks)
        elif mode == ExecutionMode.PARALLEL:
            return await self._execute_parallel(blocks)
        elif mode == ExecutionMode.STAGGERED:
            return await self._execute_staggered(blocks, stagger_delay)
        else:
            return await self._execute_sequential(blocks)
    
    async def _execute_sequential(self, blocks: List[Any]) -> List[Any]:
        """Execute blocks sequentially."""
        results = []
        for block in blocks:
            # In production, would execute actual block
            result = {"block_id": getattr(block, 'id', 'unknown'), "status": "executed"}
            results.append(result)
            await asyncio.sleep(0.05)  # Small delay between blocks
        return results
    
    async def _execute_parallel(self, blocks: List[Any]) -> List[Any]:
        """Execute blocks in parallel."""
        tasks = []
        for block in blocks:
            # In production, would execute actual block
            async def execute_block(b):
                return {"block_id": getattr(b, 'id', 'unknown'), "status": "executed"}
            tasks.append(execute_block(block))
        
        return await asyncio.gather(*tasks)
    
    async def _execute_staggered(self, blocks: List[Any], delay: float) -> List[Any]:
        """Execute blocks with staggered delays."""
        results = []
        for i, block in enumerate(blocks):
            if i > 0:
                await asyncio.sleep(delay)
            # In production, would execute actual block
            result = {"block_id": getattr(block, 'id', 'unknown'), "status": "executed"}
            results.append(result)
        return results
    
    def schedule_execution(
        self,
        block_id: str,
        dependencies: List[str],
        execution_time: Optional[datetime] = None
    ) -> Dict:
        """
        Schedule a block for execution.
        
        Args:
            block_id: Block identifier
            dependencies: List of block IDs that must complete first
            execution_time: Optional scheduled execution time
            
        Returns:
            Schedule information
        """
        schedule = {
            "block_id": block_id,
            "dependencies": dependencies,
            "execution_time": execution_time.isoformat() if execution_time else None,
            "scheduled_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.execution_history.append(schedule)
        return schedule
