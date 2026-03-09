import click
from ..dispatch import dispatch


@click.group("pipeline")
def pipeline():
    """Data pipeline operations."""
    pass


@pipeline.command()
@click.option("--mode", type=click.Choice(["batch", "watch"]), default="batch")
@click.option("--interval", default=30)
@click.option("--collector", default=None)
def run(mode, interval, collector):
    """Run the data pipeline."""
    args = ["-m", "src.pipeline", "--mode", mode, "--interval", str(interval)]
    if collector:
        args.extend(["--collector", collector])
    dispatch("data-pipeline", args)
