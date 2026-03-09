"""
Command-line interface for Nightshade Tracker.
"""

import click
import yaml
from pathlib import Path
import json
from typing import Optional

from core.image_processor import ImageProcessor
from core.text_processor import TextProcessor
from core.watermarking import RobustWatermarker
from core.poisoning import AdversarialPoisoner
from core.text_poisoning import TextPoisoner
from core.text_watermarking import TextWatermarker
from core.optimizer import MultiObjectiveOptimizer
from core.detector import WatermarkDetector
from database.registry import ImageRegistry
from utils.perceptual_hash import compute_multiple_hashes
import hashlib


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


@click.group()
@click.option('--config', default='config.yaml', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Nightshade Tracker: Poisoning-Concurrent Watermarking System"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)


@cli.command()
@click.option('--input', '-i', required=True, help='Input image path')
@click.option('--output', '-o', required=True, help='Output image path')
@click.option('--poison-strength', default=0.1, type=float, help='Poison strength (0.0-1.0)')
@click.option('--watermark-strength', default=0.01, type=float, help='Watermark strength (0.0-1.0)')
@click.option('--alpha', default=0.5, type=float, help='Balance parameter (0.0=watermark, 1.0=poison)')
@click.option('--db-path', default='registry.db', help='Database path')
@click.pass_context
def process(ctx, input, output, poison_strength, watermark_strength, alpha, db_path):
    """Process an image: add poison + watermark"""
    config = ctx.obj['config']
    
    # Override with config if available
    if 'poisoning' in config:
        poison_strength = config['poisoning'].get('strength', poison_strength)
    if 'watermark' in config:
        watermark_strength = config.get('watermark_strength', watermark_strength)
    if 'optimization' in config:
        alpha = config['optimization'].get('alpha', alpha)
    
    click.echo(f"Processing image: {input}")
    
    # Initialize components
    image_processor = ImageProcessor()
    registry = ImageRegistry(db_path)
    
    # Load image
    image = image_processor.load_image(input)
    image_info = image_processor.get_image_info(image)
    
    # Initialize watermarker and poisoner
    watermark_config = config.get('watermark', {})
    watermarker = RobustWatermarker(
        uuid_bits=watermark_config.get('uuid_bits', 256),
        redundancy_factor=watermark_config.get('redundancy_factor', 15),
        ecc_enabled=watermark_config.get('ecc_enabled', True),
        ecc_redundancy=watermark_config.get('ecc_redundancy', 0.3)
    )
    
    poison_config = config.get('poisoning', {})
    poisoner = AdversarialPoisoner(
        strength=poison_strength,
        epsilon=poison_config.get('epsilon', 0.03),
        target_class=poison_config.get('target_class')
    )
    
    # Optimize (combine poison + watermark)
    optimizer = MultiObjectiveOptimizer(alpha=alpha)
    optimized_image, metrics = optimizer.optimize_simple(
        image, watermarker, poisoner,
        poison_strength=poison_strength,
        watermark_strength=watermark_strength
    )
    
    # Save processed image
    image_processor.save_image(optimized_image, output)
    
    # Compute hashes
    hashes = compute_multiple_hashes(optimized_image)
    
    # Register in database
    image_id = registry.register_image(
        original_filename=Path(input).name,
        uuid=watermarker.get_uuid(),
        phash=hashes['phash'],
        processed_filename=Path(output).name,
        phash_large=hashes.get('phash_large'),
        dhash=hashes.get('dhash'),
        whash=hashes.get('whash'),
        file_path=str(Path(output).absolute()),
        file_size=Path(output).stat().st_size if Path(output).exists() else None,
        image_width=image_info['width'],
        image_height=image_info['height'],
        format=image_info['format'],
        poison_strength=poison_strength,
        watermark_strength=watermark_strength,
        metadata={
            'metrics': metrics,
            'alpha': alpha
        }
    )
    
    click.echo(f"✓ Image processed and saved to: {output}")
    click.echo(f"✓ UUID: {watermarker.get_uuid()}")
    click.echo(f"✓ Registered in database (ID: {image_id})")
    click.echo(f"✓ Poison loss: {metrics['poison_loss'][0]:.4f}")
    click.echo(f"✓ Watermark loss: {metrics['watermark_loss'][0]:.4f}")


@cli.command()
@click.option('--input', '-i', required=True, help='Input image path to check')
@click.option('--db-path', default='registry.db', help='Database path')
@click.option('--watermark-strength', default=0.01, type=float, help='Watermark strength')
@click.pass_context
def detect(ctx, input, db_path, watermark_strength):
    """Detect watermark in an image"""
    config = ctx.obj['config']
    
    if 'watermark' in config:
        watermark_strength = config.get('watermark_strength', watermark_strength)
    
    click.echo(f"Detecting watermark in: {input}")
    
    # Initialize detector
    registry = ImageRegistry(db_path)
    detector = WatermarkDetector(registry, watermark_strength=watermark_strength)
    
    # Detect
    result = detector.detect(input)
    
    # Display results
    if result['detected']:
        click.echo("✓ Watermark DETECTED!")
        click.echo(f"  UUID: {result['extracted_uuid']}")
        click.echo(f"  Confidence: {result['confidence']:.2%}")
        if result['match']:
            match = result['match']
            click.echo(f"  Original file: {match.get('original_filename', 'Unknown')}")
            click.echo(f"  Registered: {match.get('created_at', 'Unknown')}")
    else:
        click.echo("✗ No watermark detected")
        if result['extracted_uuid']:
            click.echo(f"  Extracted UUID: {result['extracted_uuid']} (not in registry)")


@cli.command()
@click.option('--dataset', '-d', required=True, help='Dataset directory to scan')
@click.option('--output', '-o', default='matches.json', help='Output JSON file for matches')
@click.option('--db-path', default='registry.db', help='Database path')
@click.option('--recursive/--no-recursive', default=True, help='Scan recursively')
@click.option('--watermark-strength', default=0.01, type=float, help='Watermark strength')
@click.option('--dataset-name', help='Dataset name for tracking (e.g., "LAION-5B")')
@click.option('--source-type', default='dataset', help='Source type (dataset, web, local, api)')
@click.pass_context
def scan(ctx, dataset, output, db_path, recursive, watermark_strength, dataset_name, source_type):
    """Scan a dataset directory for watermarked images"""
    config = ctx.obj['config']
    
    if 'watermark' in config:
        watermark_strength = config.get('watermark_strength', watermark_strength)
    
    click.echo(f"Scanning dataset: {dataset}")
    if dataset_name:
        click.echo(f"Tracking as dataset: {dataset_name}")
    
    # Initialize detector
    registry = ImageRegistry(db_path)
    detector = WatermarkDetector(registry, watermark_strength=watermark_strength)
    
    # Scan with tracking info
    results = detector.scan_directory(
        dataset, 
        recursive=recursive,
        source_dataset=dataset_name,
        source_type=source_type
    )
    
    # Save results
    with open(output, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    click.echo(f"✓ Scan complete: {len(results)} matches found")
    click.echo(f"✓ Results saved to: {output}")
    
    # Display summary
    if results:
        click.echo("\nMatches found:")
        for i, result in enumerate(results[:10], 1):  # Show first 10
            click.echo(f"  {i}. {result['image_path']} (confidence: {result['confidence']:.2%})")
            if result.get('match'):
                click.echo(f"      Original: {result['match'].get('original_filename', 'Unknown')}")
        if len(results) > 10:
            click.echo(f"  ... and {len(results) - 10} more")


@cli.command()
@click.option('--db-path', default='registry.db', help='Database path')
@click.pass_context
def list(ctx, db_path):
    """List all registered images"""
    registry = ImageRegistry(db_path)
    images = registry.get_all_images()
    
    if not images:
        click.echo("No images registered")
        return
    
    click.echo(f"Registered images ({len(images)}):")
    for img in images:
        click.echo(f"  [{img['id']}] {img['original_filename']}")
        click.echo(f"      UUID: {img['uuid']}")
        click.echo(f"      Created: {img['created_at']}")


@cli.command()
@click.option('--uuid', help='UUID to look up')
@click.option('--id', type=int, help='Image ID to look up')
@click.option('--db-path', default='registry.db', help='Database path')
@click.pass_context
def lookup(ctx, uuid, id, db_path):
    """Look up image in registry"""
    registry = ImageRegistry(db_path)
    
    if uuid:
        match = registry.lookup_by_uuid(uuid)
        if match:
            click.echo(f"Found image:")
            click.echo(f"  ID: {match['id']}")
            click.echo(f"  Original: {match['original_filename']}")
            click.echo(f"  UUID: {match['uuid']}")
            click.echo(f"  Created: {match['created_at']}")
        else:
            click.echo(f"No image found with UUID: {uuid}")
    elif id:
        images = registry.get_all_images()
        match = next((img for img in images if img['id'] == id), None)
        if match:
            click.echo(f"Found image:")
            click.echo(f"  ID: {match['id']}")
            click.echo(f"  Original: {match['original_filename']}")
            click.echo(f"  UUID: {match['uuid']}")
        else:
            click.echo(f"No image found with ID: {id}")
    else:
        click.echo("Please provide --uuid or --id")


@cli.command()
@click.option('--id', type=int, required=True, help='Image ID to get trail for')
@click.option('--db-path', default='registry.db', help='Database path')
@click.option('--output', '-o', help='Output JSON file for trail')
@click.pass_context
def trail(ctx, id, db_path, output):
    """Get complete usage trail for an image"""
    registry = ImageRegistry(db_path)
    
    # Get usage trail
    trail_data = registry.get_usage_trail(id)
    
    if 'error' in trail_data:
        click.echo(f"Error: {trail_data['error']}")
        return
    
    # Display trail
    image = trail_data['image']
    click.echo(f"Usage Trail for Image ID {id}")
    click.echo(f"  Original: {image.get('original_filename', 'Unknown')}")
    click.echo(f"  UUID: {image.get('uuid', 'Unknown')}")
    click.echo(f"  Created: {image.get('created_at', 'Unknown')}")
    click.echo(f"\nTracking Statistics:")
    click.echo(f"  Total Detections: {trail_data['total_detections']}")
    click.echo(f"  First Detected: {trail_data.get('first_detected', 'Never')}")
    click.echo(f"  Last Detected: {trail_data.get('last_detected', 'Never')}")
    
    if trail_data['datasets']:
        click.echo(f"\n  Found in Datasets:")
        for dataset, count in trail_data['datasets'].items():
            click.echo(f"    - {dataset}: {count} times")
    
    if trail_data['sources']:
        click.echo(f"\n  Found in Sources:")
        for source_type, count in trail_data['sources'].items():
            click.echo(f"    - {source_type}: {count} times")
    
    if trail_data['detections']:
        click.echo(f"\n  Recent Detections:")
        for det in trail_data['detections'][:5]:  # Show last 5
            click.echo(f"    - {det.get('detected_at', 'Unknown')}: {det.get('source_path', 'Unknown')}")
            if det.get('source_dataset'):
                click.echo(f"      Dataset: {det['source_dataset']}")
            if det.get('source_url'):
                click.echo(f"      URL: {det['source_url']}")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(trail_data, f, indent=2, default=str)
        click.echo(f"\n✓ Trail saved to: {output}")


@cli.command()
@click.option('--db-path', default='registry.db', help='Database path')
@click.option('--output', '-o', help='Output JSON file for summary')
@click.pass_context
def summary(ctx, db_path, output):
    """Get tracking summary and statistics"""
    registry = ImageRegistry(db_path)
    
    summary_data = registry.get_tracking_summary()
    
    click.echo("Tracking Summary")
    click.echo("=" * 50)
    click.echo(f"Total Images Tracked: {summary_data['total_images_tracked']}")
    click.echo(f"Total Detections: {summary_data['total_detections']}")
    click.echo(f"Unique Datasets: {summary_data['unique_datasets']}")
    
    if summary_data['detections_by_source_type']:
        click.echo(f"\nDetections by Source Type:")
        for source_type, count in summary_data['detections_by_source_type'].items():
            click.echo(f"  {source_type}: {count}")
    
    if summary_data['detections_by_dataset']:
        click.echo(f"\nDetections by Dataset:")
        for dataset, count in summary_data['detections_by_dataset'].items():
            click.echo(f"  {dataset}: {count}")
    
    if summary_data['datasets']:
        click.echo(f"\nAll Datasets Found:")
        for dataset in summary_data['datasets']:
            click.echo(f"  - {dataset}")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)
        click.echo(f"\n✓ Summary saved to: {output}")


@cli.command()
@click.option('--id', type=int, help='Image ID (optional, shows all if not provided)')
@click.option('--dataset', help='Filter by dataset name')
@click.option('--source-type', help='Filter by source type')
@click.option('--db-path', default='registry.db', help='Database path')
@click.option('--output', '-o', help='Output JSON file')
@click.pass_context
def detections(ctx, id, dataset, source_type, db_path, output):
    """List detection logs"""
    registry = ImageRegistry(db_path)
    
    detections_list = registry.get_detections(
        image_id=id,
        source_dataset=dataset,
        source_type=source_type
    )
    
    if not detections_list:
        click.echo("No detections found")
        return
    
    click.echo(f"Found {len(detections_list)} detection(s)")
    
    for det in detections_list[:20]:  # Show first 20
        click.echo(f"\nDetection ID: {det['id']}")
        click.echo(f"  Image ID: {det.get('image_id', 'Unknown')}")
        click.echo(f"  Detected: {det.get('detected_at', 'Unknown')}")
        click.echo(f"  Source: {det.get('source_path', 'Unknown')}")
        if det.get('source_dataset'):
            click.echo(f"  Dataset: {det['source_dataset']}")
        if det.get('source_url'):
            click.echo(f"  URL: {det['source_url']}")
        click.echo(f"  Confidence: {det.get('confidence', 0):.2%}")
    
    if len(detections_list) > 20:
        click.echo(f"\n... and {len(detections_list) - 20} more")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(detections_list, f, indent=2, default=str)
        click.echo(f"\n✓ Detections saved to: {output}")


@cli.command()
@click.option('--input', '-i', required=True, help='Input text file path')
@click.option('--output', '-o', required=True, help='Output text file path')
@click.option('--poison-strength', default=0.1, type=float, help='Poison strength (0.0-1.0)')
@click.option('--capitalization-rate', default=0.15, type=float, help='Capitalization change rate (0.0-1.0)')
@click.option('--word-order-rate', default=0.1, type=float, help='Word order swap rate (0.0-1.0)')
@click.option('--spelling-rate', default=0.05, type=float, help='Spelling variation rate (0.0-1.0)')
@click.option('--watermark-strength', default=0.01, type=float, help='Watermark strength (0.0-1.0)')
@click.option('--db-path', default='registry.db', help='Database path')
@click.pass_context
def process_text(ctx, input, output, poison_strength, capitalization_rate, word_order_rate, spelling_rate, watermark_strength, db_path):
    """Process a text file: add poison + watermark"""
    config = ctx.obj['config']
    
    click.echo(f"Processing text file: {input}")
    
    # Initialize components
    text_processor = TextProcessor()
    registry = ImageRegistry(db_path)
    
    # Load text
    text = text_processor.load_text(input)
    text_info = text_processor.get_text_info(text)
    
    # Initialize text poisoner with subtle modifications
    poison_config = config.get('text_poisoning', {})
    poisoner = TextPoisoner(
        strength=poison_strength,
        capitalization_rate=capitalization_rate or poison_config.get('capitalization_rate', 0.15),
        word_order_rate=word_order_rate or poison_config.get('word_order_rate', 0.1),
        spelling_rate=spelling_rate or poison_config.get('spelling_rate', 0.05)
    )
    
    # Initialize text watermarker
    watermark_config = config.get('text_watermark', {})
    watermarker = TextWatermarker(
        uuid_bits=watermark_config.get('uuid_bits', 256),
        redundancy_factor=watermark_config.get('redundancy_factor', 10),
        ecc_enabled=watermark_config.get('ecc_enabled', True),
        ecc_redundancy=watermark_config.get('ecc_redundancy', 0.3)
    )
    
    # Apply subtle poisoning (default method)
    poisoned_text = poisoner.poison_text(text, method="subtle")
    
    # Apply watermarking
    watermarked_text = watermarker.embed(poisoned_text)
    
    # Save processed text
    text_processor.save_text(watermarked_text, output)
    
    # Compute hash
    text_hash = hashlib.sha256(watermarked_text.encode('utf-8')).hexdigest()
    
    # Compute poison metrics
    poison_metrics = poisoner.compute_poison_metrics(text, poisoned_text)
    
    # Register in database
    text_id = registry.register_text(
        original_filename=Path(input).name,
        uuid=watermarker.get_uuid(),
        text_hash=text_hash,
        processed_filename=Path(output).name,
        file_path=str(Path(output).absolute()),
        file_size=Path(output).stat().st_size if Path(output).exists() else None,
        word_count=text_info['word_count'],
        char_count=text_info['char_count'],
        line_count=text_info['line_count'],
        format=text_info['format'],
        poison_strength=poison_strength,
        watermark_strength=watermark_strength,
        metadata={
            'poison_metrics': poison_metrics,
            'capitalization_rate': capitalization_rate,
            'word_order_rate': word_order_rate,
            'spelling_rate': spelling_rate
        }
    )
    
    click.echo(f"✓ Text processed and saved to: {output}")
    click.echo(f"✓ UUID: {watermarker.get_uuid()}")
    click.echo(f"✓ Registered in database (ID: {text_id})")
    click.echo(f"✓ Capitalization changes: {poison_metrics['capitalization_changes']}")
    click.echo(f"✓ Spelling variations: {poison_metrics['spelling_changes']}")
    click.echo(f"✓ Hash test: {'PASSED' if poison_metrics['hash_test_passed'] else 'FAILED'}")
    if poison_metrics['hash_test_passed']:
        click.echo(f"  Original hash: {poison_metrics['original_hash'][:16]}...")
        click.echo(f"  Poisoned hash: {poison_metrics['poisoned_hash'][:16]}...")


@cli.command()
@click.option('--input', '-i', required=True, help='Input text file path to check')
@click.option('--db-path', default='registry.db', help='Database path')
@click.pass_context
def detect_text(ctx, input, db_path):
    """Detect watermark in a text file"""
    config = ctx.obj['config']
    
    click.echo(f"Detecting watermark in: {input}")
    
    # Initialize components
    text_processor = TextProcessor()
    registry = ImageRegistry(db_path)
    watermarker = TextWatermarker()
    
    # Load text
    text = text_processor.load_text(input)
    
    # Extract watermark
    extracted_uuid = watermarker.extract(text)
    
    if extracted_uuid:
        click.echo("✓ Watermark DETECTED!")
        click.echo(f"  UUID: {extracted_uuid}")
        
        # Look up in registry
        match = registry.lookup_text_by_uuid(extracted_uuid)
        if match:
            click.echo(f"  Original file: {match.get('original_filename', 'Unknown')}")
            click.echo(f"  Registered: {match.get('created_at', 'Unknown')}")
            click.echo(f"  Confidence: High (UUID match)")
        else:
            click.echo(f"  UUID not found in registry (may be from external source)")
    else:
        click.echo("✗ No watermark detected")


@cli.command()
@click.option('--db-path', default='registry.db', help='Database path')
@click.pass_context
def list_text(ctx, db_path):
    """List all registered text files"""
    registry = ImageRegistry(db_path)
    text_files = registry.get_all_text_files()
    
    if not text_files:
        click.echo("No text files registered")
        return
    
    click.echo(f"Registered text files ({len(text_files)}):")
    for txt in text_files:
        click.echo(f"  [{txt['id']}] {txt['original_filename']}")
        click.echo(f"      UUID: {txt['uuid']}")
        click.echo(f"      Created: {txt['created_at']}")


if __name__ == '__main__':
    cli()
