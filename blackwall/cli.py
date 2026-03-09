"""
Blackwall CLI: Unified interface for text and image protection.
"""

import click
from pathlib import Path
from core.unified_processor import UnifiedProcessor
from database.registry import BlackwallRegistry


@click.group()
def cli():
    """Blackwall: AI Dungeon for Text & Image Protection"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='Input text file')
@click.option('--output', '-o', required=True, help='Output text file')
@click.option('--poison-strength', default=0.1, type=float, help='Poison strength')
def process_text(input, output, poison_strength):
    """Process text: add poison + watermark"""
    click.echo(f"Processing text: {input}")
    
    processor = UnifiedProcessor(poison_strength=poison_strength)
    registry = BlackwallRegistry()
    
    # Read text
    with open(input, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Process
    processed_text, metadata = processor.process_text(text)
    
    # Save
    with open(output, 'w', encoding='utf-8') as f:
        f.write(processed_text)
    
    # Register
    registry.register_content(
        original_path=input,
        processed_path=output,
        content_type="text",
        uuid=metadata['uuid'],
        metadata=metadata
    )
    
    click.echo(f"✓ Text processed and saved to: {output}")
    click.echo(f"✓ UUID: {metadata['uuid']}")


@cli.command()
@click.option('--input', '-i', required=True, help='Input image file')
@click.option('--output', '-o', required=True, help='Output image file')
@click.option('--poison-strength', default=0.1, type=float, help='Poison strength')
def process_image(input, output, poison_strength):
    """Process image: add poison + watermark"""
    click.echo(f"Processing image: {input}")
    
    processor = UnifiedProcessor(poison_strength=poison_strength)
    registry = BlackwallRegistry()
    
    # Process
    metadata = processor.process_image(input, output)
    
    # Register
    registry.register_content(
        original_path=input,
        processed_path=output,
        content_type="image",
        uuid=metadata['uuid'],
        metadata=metadata
    )
    
    click.echo(f"✓ Image processed and saved to: {output}")
    click.echo(f"✓ UUID: {metadata['uuid']}")


@cli.command()
@click.option('--input', '-i', required=True, help='Input file to check')
@click.option('--type', 'content_type', type=click.Choice(['text', 'image', 'auto']),
              default='auto', help='Content type')
def detect(input, content_type):
    """Detect watermark in content"""
    click.echo(f"Detecting watermark in: {input}")
    
    processor = UnifiedProcessor()
    
    # Auto-detect type
    if content_type == 'auto':
        path = Path(input)
        if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            content_type = 'image'
        else:
            content_type = 'text'
    
    # Detect
    if content_type == 'text':
        with open(input, 'r', encoding='utf-8') as f:
            text = f.read()
        result = processor.detect_text(text)
    else:
        result = processor.detect_image(input)
    
    if result['detected']:
        click.echo(f"✓ Watermark DETECTED!")
        click.echo(f"  UUID: {result['uuid']}")
    else:
        click.echo("✗ No watermark detected")


if __name__ == '__main__':
    cli()
