"""
Example usage of Nightshade Tracker
"""

from core.image_processor import ImageProcessor
from core.watermarking import RobustWatermarker
from core.poisoning import AdversarialPoisoner
from core.optimizer import MultiObjectiveOptimizer
from core.detector import WatermarkDetector
from database.registry import ImageRegistry
from utils.perceptual_hash import compute_multiple_hashes


def example_process_image(input_path: str, output_path: str):
    """Example: Process an image with poison + watermark"""
    print(f"Processing {input_path}...")
    
    # Initialize components
    processor = ImageProcessor()
    watermarker = RobustWatermarker(
        uuid_bits=256,
        redundancy_factor=15,
        ecc_enabled=True
    )
    poisoner = AdversarialPoisoner(strength=0.1, epsilon=0.03)
    optimizer = MultiObjectiveOptimizer(alpha=0.5)
    registry = ImageRegistry()
    
    # Load image
    image = processor.load_image(input_path)
    image_info = processor.get_image_info(image)
    print(f"Image size: {image_info['width']}x{image_info['height']}")
    
    # Process
    optimized, metrics = optimizer.optimize_simple(
        image, watermarker, poisoner,
        poison_strength=0.1,
        watermark_strength=0.01
    )
    
    # Save
    processor.save_image(optimized, output_path)
    print(f"Saved to {output_path}")
    
    # Compute hashes
    hashes = compute_multiple_hashes(optimized)
    
    # Register
    image_id = registry.register_image(
        original_filename=input_path,
        uuid=watermarker.get_uuid(),
        phash=hashes['phash'],
        processed_filename=output_path,
        image_width=image_info['width'],
        image_height=image_info['height'],
        format=image_info['format']
    )
    
    print(f"Registered in database (ID: {image_id})")
    print(f"UUID: {watermarker.get_uuid()}")
    print(f"Metrics: {metrics}")
    
    return watermarker.get_uuid()


def example_detect_watermark(image_path: str):
    """Example: Detect watermark in an image"""
    print(f"Detecting watermark in {image_path}...")
    
    registry = ImageRegistry()
    detector = WatermarkDetector(registry)
    
    result = detector.detect(image_path)
    
    if result['detected']:
        print("✓ Watermark detected!")
        print(f"  UUID: {result['extracted_uuid']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        if result['match']:
            match = result['match']
            print(f"  Original: {match.get('original_filename')}")
    else:
        print("✗ No watermark detected")
    
    return result


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python example.py process <input> <output>")
        print("  python example.py detect <image>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'process':
        if len(sys.argv) < 4:
            print("Usage: python example.py process <input> <output>")
            sys.exit(1)
        example_process_image(sys.argv[2], sys.argv[3])
    elif command == 'detect':
        if len(sys.argv) < 3:
            print("Usage: python example.py detect <image>")
            sys.exit(1)
        example_detect_watermark(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
