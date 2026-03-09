#!/usr/bin/env python3
"""
Basic competition example using RADICAL event-driven architecture.

Demonstrates:
- Event bus setup
- Round lifecycle
- Solution submission with diversity enforcement
- JSON-RPC critique arena
"""
import asyncio
import logging
from pathlib import Path

from src.core.event_bus import get_event_bus
from src.core.event_types import (
    RoundStarted,
    SolutionSubmitted,
    SolutionAccepted,
    SolutionRejected,
    TestStarted,
    TestCompleted,
    ScoreCalculated,
    RoundEnded,
)
from src.diversity.threshold import DiversityEnforcer, DiversityConfig
from src.rpc.server import UnixSocketRPCServer
from src.rpc.handlers import CritiqueArenaHandlers
from src.rpc.protocol import JSONRPCHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run a basic competition."""
    
    # Initialize event bus
    logger.info("Initializing event bus...")
    event_bus = get_event_bus()
    await event_bus.start()
    
    # Subscribe to key events
    def on_solution_submitted(event: SolutionSubmitted):
        logger.info(f"📦 Solution submitted: {event.solution_id} by {event.competitor_id}")
    
    def on_solution_accepted(event: SolutionAccepted):
        logger.info(f"✅ Solution accepted: {event.solution_id} (diversity: {event.diversity_score:.2f})")
    
    def on_solution_rejected(event: SolutionRejected):
        logger.warning(f"❌ Solution rejected: {event.solution_id} - {event.reason}")
    
    def on_test_completed(event: TestCompleted):
        status = "✅ PASSED" if event.passed else "❌ FAILED"
        logger.info(f"{status} Test for {event.solution_id} ({event.duration_ms}ms)")
    
    def on_score_calculated(event: ScoreCalculated):
        total = event.scores.get("total", 0.0)
        logger.info(f"📊 Score for {event.solution_id}: {total:.2f}")
    
    event_bus.subscribe(SolutionSubmitted.type, on_solution_submitted)
    event_bus.subscribe(SolutionAccepted.type, on_solution_accepted)
    event_bus.subscribe(SolutionRejected.type, on_solution_rejected)
    event_bus.subscribe(TestCompleted.type, on_test_completed)
    event_bus.subscribe(ScoreCalculated.type, on_score_calculated)
    
    # Initialize diversity enforcer
    logger.info("Initializing diversity enforcer...")
    diversity_config = DiversityConfig(
        min_similarity_threshold=0.85,
        max_cluster_size=3,
        diversity_bonus=0.1
    )
    enforcer = DiversityEnforcer(diversity_config)
    
    # Start JSON-RPC server
    logger.info("Starting JSON-RPC server...")
    handlers = CritiqueArenaHandlers()
    rpc_handler = JSONRPCHandler()
    rpc_handler.register_method("critique.request", handlers.critique_request)
    rpc_handler.register_method("critique.submit", handlers.critique_submit)
    rpc_handler.register_method("solutions.list", handlers.solutions_list)
    
    socket_path = Path(".shared-cache/critique-arena.sock")
    socket_path.parent.mkdir(parents=True, exist_ok=True)
    
    server = UnixSocketRPCServer(socket_path, rpc_handler)
    await server.start()
    logger.info(f"JSON-RPC server listening on {socket_path}")
    
    # Simulate a competition round
    logger.info("\n" + "="*60)
    logger.info("Starting Competition Round 1")
    logger.info("="*60 + "\n")
    
    # 1. Start round
    await event_bus.emit(RoundStarted(
        round_id=1,
        task_spec={
            "name": "Example Task",
            "description": "Solve problem X",
            "constraints": ["Python only", "No external deps"]
        },
        competitor_ids=["radical_1", "conservative_1", "balanced_1"]
    ))
    
    # 2. Submit solutions
    solutions = [
        ("radical_1", "sol_radical_1", Path("worktrees/wt_radical_1_r1/solution")),
        ("conservative_1", "sol_conservative_1", Path("worktrees/wt_conservative_1_r1/solution")),
        ("balanced_1", "sol_balanced_1", Path("worktrees/wt_balanced_1_r1/solution")),
    ]
    
    for competitor_id, solution_id, solution_path in solutions:
        # Emit submission event
        await event_bus.emit(SolutionSubmitted(
            competitor_id=competitor_id,
            round_id=1,
            solution_id=solution_id,
            files=[{"path": "main.py", "size": 100, "hash": f"hash_{solution_id}"}],
            worktree_path=solution_path
        ))
        
        # Check diversity (in real system, this would be handled by solution manager)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        accepted, reason, similarity, similar_ids = enforcer.check_diversity(
            1, solution_id, solution_path
        )
        
        if accepted:
            enforcer.register_solution(1, solution_id, solution_path)
            diversity_score = enforcer.calculate_diversity_score(1, solution_id, solution_path)
            
            await event_bus.emit(SolutionAccepted(
                solution_id=solution_id,
                diversity_score=diversity_score
            ))
            
            # Register with RPC handlers
            handlers.register_solution(1, {
                "solution_id": solution_id,
                "competitor_id": competitor_id,
                "round_id": 1,
                "files": []
            })
            
            # Run tests (simulated)
            await event_bus.emit(TestStarted(
                solution_id=solution_id,
                test_suite="tests/test_solution.py"
            ))
            
            await asyncio.sleep(0.1)  # Simulate test execution
            
            await event_bus.emit(TestCompleted(
                solution_id=solution_id,
                passed=True,
                output="All tests passed",
                duration_ms=1500
            ))
            
            # Calculate score (simplified)
            await event_bus.emit(ScoreCalculated(
                solution_id=solution_id,
                scores={
                    "test_score": 1.0,
                    "diversity_bonus": diversity_score * 0.1,
                    "total": 1.0 + diversity_score * 0.1
                },
                test_results={"passed": True}
            ))
        else:
            await event_bus.emit(SolutionRejected(
                solution_id=solution_id,
                reason=reason,
                similarity_to_existing=similarity,
                similar_solution_ids=similar_ids
            ))
    
    # 3. Calculate convergence
    convergence, cluster_sizes = enforcer.calculate_convergence(1)
    logger.info(f"\n📈 Convergence metric: {convergence:.2f}")
    logger.info(f"📊 Cluster sizes: {cluster_sizes}")
    
    # 4. End round
    await event_bus.emit(RoundEnded(
        round_id=1,
        results={
            "convergence": convergence,
            "cluster_sizes": cluster_sizes
        }
    ))
    
    logger.info("\n" + "="*60)
    logger.info("Round 1 Completed")
    logger.info("="*60 + "\n")
    
    # Show event bus stats
    stats = event_bus.get_stats()
    logger.info(f"Event bus stats: {stats}")
    
    # Keep server running for a bit
    logger.info("JSON-RPC server running. Press Ctrl+C to stop.")
    try:
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()
        await event_bus.stop()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
