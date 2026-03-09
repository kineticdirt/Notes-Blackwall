"""
Command-line interface for worktree orchestration.
"""
import click
from pathlib import Path
from typing import Optional

from .config import ConfigValidator
from .worktree import WorktreeManager
from .competitor import CompetitorRegistry
from .artifacts import ArtifactStore
from .arena import Arena


@click.group()
@click.pass_context
def cli(ctx):
    """Worktree Orchestration v2.0.0 - Multi-agent competition system."""
    ctx.ensure_object(dict)


@cli.command()
@click.argument('config_path', type=click.Path(exists=True))
@click.pass_context
def init(ctx, config_path):
    """Initialize competition from configuration file."""
    config_path = Path(config_path)
    base_dir = config_path.parent
    
    try:
        validator = ConfigValidator()
        config = validator.validate(config_path)
        validator.validate_paths(config, base_dir)
        
        # Create cache directory
        cache_dir = base_dir / ".shared-cache"
        cache_dir.mkdir(exist_ok=True)
        
        click.echo(f"✓ Competition '{config.competition.name}' initialized")
        click.echo(f"  Rounds: {config.competition.rounds}")
        click.echo(f"  Max competitors: {config.competition.max_competitors}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def competitor():
    """Manage competitors."""
    pass


@competitor.command('register')
@click.argument('name')
@click.argument('script_path', type=click.Path(exists=True))
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def register_competitor(name, script_path, base_dir):
    """Register a new competitor."""
    base_dir = Path(base_dir)
    script_path = Path(script_path)
    cache_dir = base_dir / ".shared-cache"
    
    try:
        registry = CompetitorRegistry(cache_dir)
        competitor = registry.register_competitor(name, script_path, base_dir)
        click.echo(f"✓ Registered competitor: {competitor.competitor_id}")
        click.echo(f"  Name: {competitor.name}")
        click.echo(f"  Script: {competitor.script_path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@competitor.command('list')
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def list_competitors(base_dir):
    """List all registered competitors."""
    base_dir = Path(base_dir)
    cache_dir = base_dir / ".shared-cache"
    
    registry = CompetitorRegistry(cache_dir)
    competitors = registry.list_competitors()
    
    if not competitors:
        click.echo("No competitors registered.")
        return
    
    for competitor in competitors:
        click.echo(f"{competitor.competitor_id}: {competitor.name}")


@cli.group()
def worktree():
    """Manage worktrees."""
    pass


@worktree.command('create')
@click.argument('competitor_id')
@click.argument('round_num', type=int)
@click.option('--base-dir', type=click.Path(exists=True), default='.')
@click.option('--config', type=click.Path(exists=True))
def create_worktree(competitor_id, round_num, base_dir, config):
    """Create a worktree for a competitor."""
    base_dir = Path(base_dir)
    
    # Load config if provided
    if config:
        validator = ConfigValidator()
        cfg = validator.validate(Path(config))
        worktree_base = base_dir / cfg.worktree.base_path
        template_path = base_dir / cfg.worktree.template_path if cfg.worktree.template_path else None
    else:
        worktree_base = base_dir / "worktrees"
        template_path = None
    
    try:
        manager = WorktreeManager(worktree_base, template_path)
        worktree = manager.create_worktree(competitor_id, round_num)
        click.echo(f"✓ Created worktree: {worktree.path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def arena():
    """Competition arena operations."""
    pass


@arena.command('start-round')
@click.argument('round_num', type=int)
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def start_round(round_num, config, base_dir):
    """Start a competition round."""
    base_dir = Path(base_dir)
    config_path = Path(config)
    
    validator = ConfigValidator()
    cfg = validator.validate(config_path)
    
    cache_dir = base_dir / ".shared-cache"
    worktree_base = base_dir / cfg.worktree.base_path
    template_path = base_dir / cfg.worktree.template_path if cfg.worktree.template_path else None
    
    worktree_manager = WorktreeManager(worktree_base, template_path)
    competitor_registry = CompetitorRegistry(cache_dir)
    artifact_store = ArtifactStore(cache_dir)
    arena = Arena(worktree_manager, competitor_registry, artifact_store, cfg)
    
    try:
        arena.start_round(round_num)
        click.echo(f"✓ Round {round_num} started")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@arena.command('submit-solution')
@click.argument('competitor_id')
@click.argument('round_num', type=int)
@click.argument('solution_path', type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def submit_solution(competitor_id, round_num, solution_path, config, base_dir):
    """Submit a solution."""
    base_dir = Path(base_dir)
    config_path = Path(config)
    solution_path = Path(solution_path)
    
    validator = ConfigValidator()
    cfg = validator.validate(config_path)
    
    cache_dir = base_dir / ".shared-cache"
    worktree_base = base_dir / cfg.worktree.base_path
    template_path = base_dir / cfg.worktree.template_path if cfg.worktree.template_path else None
    
    worktree_manager = WorktreeManager(worktree_base, template_path)
    competitor_registry = CompetitorRegistry(cache_dir)
    artifact_store = ArtifactStore(cache_dir)
    arena = Arena(worktree_manager, competitor_registry, artifact_store, cfg)
    
    try:
        artifact_id = arena.submit_solution(competitor_id, round_num, solution_path)
        click.echo(f"✓ Solution submitted: {artifact_id}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@arena.command('test')
@click.argument('round_num', type=int)
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def test_round(round_num, config, base_dir):
    """Run tests on round solutions."""
    base_dir = Path(base_dir)
    config_path = Path(config)
    
    validator = ConfigValidator()
    cfg = validator.validate(config_path)
    
    cache_dir = base_dir / ".shared-cache"
    worktree_base = base_dir / cfg.worktree.base_path
    template_path = base_dir / cfg.worktree.template_path if cfg.worktree.template_path else None
    
    worktree_manager = WorktreeManager(worktree_base, template_path)
    competitor_registry = CompetitorRegistry(cache_dir)
    artifact_store = ArtifactStore(cache_dir)
    arena = Arena(worktree_manager, competitor_registry, artifact_store, cfg)
    
    try:
        results = arena.test_round(round_num)
        click.echo(f"✓ Tests completed for round {round_num}")
        for result in results['results']:
            status = "PASS" if result['test_passed'] else "FAIL"
            click.echo(f"  {result['competitor_id']}: {status}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@arena.command('end-round')
@click.argument('round_num', type=int)
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def end_round(round_num, config, base_dir):
    """End a round and collect results."""
    base_dir = Path(base_dir)
    config_path = Path(config)
    
    validator = ConfigValidator()
    cfg = validator.validate(config_path)
    
    cache_dir = base_dir / ".shared-cache"
    worktree_base = base_dir / cfg.worktree.base_path
    template_path = base_dir / cfg.worktree.template_path if cfg.worktree.template_path else None
    
    worktree_manager = WorktreeManager(worktree_base, template_path)
    competitor_registry = CompetitorRegistry(cache_dir)
    artifact_store = ArtifactStore(cache_dir)
    arena = Arena(worktree_manager, competitor_registry, artifact_store, cfg)
    
    try:
        results = arena.end_round(round_num)
        click.echo(f"✓ Round {round_num} completed")
        click.echo(f"  Results stored in: {cache_dir / 'rounds' / f'round_{round_num:03d}' / 'results.json'}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def artifacts():
    """Manage artifacts."""
    pass


@artifacts.command('list')
@click.argument('round_num', type=int)
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def list_artifacts(round_num, base_dir):
    """List artifacts for a round."""
    base_dir = Path(base_dir)
    cache_dir = base_dir / ".shared-cache"
    
    artifact_store = ArtifactStore(cache_dir)
    artifacts = artifact_store.list_artifacts(round_num)
    
    click.echo(f"Round {round_num} artifacts:")
    click.echo(f"  Solutions: {len(artifacts['solutions'])}")
    click.echo(f"  Critiques: {len(artifacts['critiques'])}")


@cli.command()
@click.option('--force', is_flag=True, help='Skip confirmation')
@click.option('--round', type=int, help='Cleanup specific round only')
@click.option('--config', type=click.Path(exists=True))
@click.option('--base-dir', type=click.Path(exists=True), default='.')
def cleanup(force, round, config, base_dir):
    """Cleanup worktrees."""
    base_dir = Path(base_dir)
    
    if config:
        validator = ConfigValidator()
        cfg = validator.validate(Path(config))
        worktree_base = base_dir / cfg.worktree.base_path
    else:
        worktree_base = base_dir / "worktrees"
    
    manager = WorktreeManager(worktree_base)
    
    if not force:
        count = len(manager.list_worktrees(round))
        if count == 0:
            click.echo("No worktrees to cleanup.")
            return
        
        if not click.confirm(f"Remove {count} worktree(s)?"):
            return
    
    try:
        count = manager.cleanup_all(round)
        click.echo(f"✓ Cleaned up {count} worktree(s)")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()
