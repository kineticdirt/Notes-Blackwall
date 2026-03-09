"""
Detection module for extracting watermarks and matching against registry.
"""

import numpy as np
from typing import Optional, Dict, Tuple
from pathlib import Path

from core.image_processor import ImageProcessor
from core.watermarking import RobustWatermarker
from utils.perceptual_hash import compute_phash, compute_multiple_hashes, hash_distance
from database.registry import ImageRegistry


class WatermarkDetector:
    """
    Detects watermarks in images and matches against registry.
    """
    
    def __init__(self, registry: ImageRegistry, watermark_strength: float = 0.01):
        """
        Initialize detector.
        
        Args:
            registry: ImageRegistry instance
            watermark_strength: Watermark strength used (should match embedding)
        """
        self.registry = registry
        self.watermark_strength = watermark_strength
        self.image_processor = ImageProcessor()
        self.watermarker = RobustWatermarker()
    
    def detect(self, image_path: str,
               source_url: Optional[str] = None,
               source_dataset: Optional[str] = None,
               source_type: Optional[str] = None,
               context_metadata: Optional[Dict] = None) -> Dict:
        """
        Detect watermark in image and match against registry.
        Enhanced for tracking usage trails.
        
        Args:
            image_path: Path to image file
            source_url: URL where image was found (if web source)
            source_dataset: Dataset name (e.g., "LAION-5B")
            source_type: Type of source ("web", "dataset", "local", "api")
            context_metadata: Additional context information
            
        Returns:
            Dictionary with detection results
        """
        # Load image
        image = self.image_processor.load_image(image_path)
        image_info = self.image_processor.get_image_info(image)
        
        # Extract UUID
        extracted_uuid = self.watermarker.extract(image, strength=self.watermark_strength)
        
        # Compute perceptual hashes
        hashes = compute_multiple_hashes(image)
        
        # Look up in registry
        match = None
        confidence = 0.0
        
        if extracted_uuid:
            # Look up by UUID
            match = self.registry.lookup_by_uuid(extracted_uuid)
            if match:
                confidence = 1.0  # Perfect UUID match
            else:
                # Try pHash matching
                phash_matches = self.registry.lookup_by_phash(
                    hashes['phash'], threshold=5
                )
                if phash_matches:
                    match = phash_matches[0]
                    # Confidence based on hash distance
                    distance = match.get('phash_distance', 10)
                    confidence = max(0.0, 1.0 - (distance / 10.0))
        else:
            # No UUID found, try pHash only
            phash_matches = self.registry.lookup_by_phash(
                hashes['phash'], threshold=5
            )
            if phash_matches:
                match = phash_matches[0]
                distance = match.get('phash_distance', 10)
                confidence = max(0.0, 1.0 - (distance / 10.0))
        
        result = {
            'image_path': image_path,
            'extracted_uuid': extracted_uuid,
            'hashes': hashes,
            'match': match,
            'confidence': confidence,
            'detected': match is not None,
            'source_url': source_url,
            'source_dataset': source_dataset,
            'source_type': source_type
        }
        
        # Log detection if match found (with enhanced tracking info)
        if match:
            # Get file size if available
            file_size = None
            try:
                from pathlib import Path
                file_size = Path(image_path).stat().st_size
            except:
                pass
            
            self.registry.log_detection(
                image_id=match['id'],
                detected_uuid=extracted_uuid or '',
                detected_phash=hashes['phash'],
                source_path=image_path,
                confidence=confidence,
                source_url=source_url,
                source_dataset=source_dataset,
                source_type=source_type or 'local',
                file_size=file_size,
                image_width=image_info.get('width'),
                image_height=image_info.get('height'),
                format=image_info.get('format'),
                context_metadata=context_metadata
            )
        
        return result
    
    def scan_directory(self, directory: str, 
                      extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.webp'),
                      recursive: bool = True,
                      source_dataset: Optional[str] = None,
                      source_type: str = 'local') -> list:
        """
        Scan directory for watermarked images.
        Enhanced for tracking with dataset/source information.
        
        Args:
            directory: Directory to scan
            extensions: File extensions to check
            recursive: Whether to scan recursively
            source_dataset: Dataset name (e.g., "LAION-5B", "HuggingFace")
            source_type: Type of source ("web", "dataset", "local", "api")
            
        Returns:
            List of detection results
        """
        directory_path = Path(directory)
        results = []
        
        if recursive:
            image_files = []
            for ext in extensions:
                image_files.extend(directory_path.rglob(f'*{ext}'))
                image_files.extend(directory_path.rglob(f'*{ext.upper()}'))
        else:
            image_files = []
            for ext in extensions:
                image_files.extend(directory_path.glob(f'*{ext}'))
                image_files.extend(directory_path.glob(f'*{ext.upper()}'))
        
        for image_file in image_files:
            try:
                result = self.detect(
                    str(image_file),
                    source_dataset=source_dataset or directory_path.name,
                    source_type=source_type
                )
                if result['detected']:
                    results.append(result)
            except Exception as e:
                # Skip files that can't be processed
                print(f"Error processing {image_file}: {e}")
                continue
        
        return results
