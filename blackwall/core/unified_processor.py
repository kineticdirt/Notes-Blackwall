"""
Unified processor for both text and image content.
"""

from typing import Union, Tuple, Dict
from pathlib import Path

# Import text modules
from core.text_poisoning import TextPoisoner
from core.text_watermarking import TextWatermarker

# Import image modules (from nightshade-tracker)
import sys
nightshade_path = Path(__file__).parent.parent.parent / "nightshade-tracker"
if nightshade_path.exists():
    sys.path.insert(0, str(nightshade_path))
    from core.poisoning import AdversarialPoisoner
    from core.watermarking import RobustWatermarker
    from core.image_processor import ImageProcessor
else:
    # Placeholder if nightshade-tracker not available
    AdversarialPoisoner = None
    RobustWatermarker = None
    ImageProcessor = None


class UnifiedProcessor:
    """
    Processes both text and image content with poisoning and watermarking.
    """
    
    def __init__(self, poison_strength: float = 0.1,
                 watermark_strength: float = 0.01):
        """
        Initialize unified processor.
        
        Args:
            poison_strength: Strength of poisoning
            watermark_strength: Strength of watermarking
        """
        self.poison_strength = poison_strength
        self.watermark_strength = watermark_strength
        
        # Initialize text processors
        self.text_poisoner = TextPoisoner(strength=poison_strength)
        self.text_watermarker = TextWatermarker()
        
        # Initialize image processors (if available)
        if AdversarialPoisoner:
            self.image_poisoner = AdversarialPoisoner(strength=poison_strength)
            self.image_watermarker = RobustWatermarker()
            self.image_processor = ImageProcessor()
        else:
            self.image_poisoner = None
            self.image_watermarker = None
            self.image_processor = None
    
    def process_text(self, text: str) -> Tuple[str, Dict]:
        """
        Process text: apply poisoning + watermarking.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (processed_text, metadata)
        """
        # Step 1: Apply watermark
        watermarked_text = self.text_watermarker.embed(text, method="unicode")
        
        # Step 2: Apply poison
        poisoned_text = self.text_poisoner.poison_text(watermarked_text)
        
        metadata = {
            "uuid": self.text_watermarker.get_uuid(),
            "poison_strength": self.poison_strength,
            "watermark_method": "unicode",
            "content_type": "text"
        }
        
        return poisoned_text, metadata
    
    def process_image(self, image_path: str, output_path: str) -> Dict:
        """
        Process image: apply poisoning + watermarking.
        
        Args:
            image_path: Input image path
            output_path: Output image path
            
        Returns:
            Metadata dictionary
        """
        if not self.image_processor:
            raise ValueError("Image processing not available (nightshade-tracker required)")
        
        # Load image
        image = self.image_processor.load_image(image_path)
        
        # Apply watermark
        watermarked = self.image_watermarker.embed(image, strength=self.watermark_strength)
        
        # Apply poison
        perturbation = self.image_poisoner.generate_perturbation(watermarked)
        poisoned = self.image_poisoner.apply_poison(watermarked, perturbation)
        
        # Save
        self.image_processor.save_image(poisoned, output_path)
        
        metadata = {
            "uuid": self.image_watermarker.get_uuid(),
            "poison_strength": self.poison_strength,
            "watermark_strength": self.watermark_strength,
            "content_type": "image"
        }
        
        return metadata
    
    def detect_text(self, text: str) -> Dict:
        """
        Detect watermark in text.
        
        Args:
            text: Text to check
            
        Returns:
            Detection result dictionary
        """
        extracted_uuid = self.text_watermarker.extract(text, method="unicode")
        
        return {
            "detected": extracted_uuid is not None,
            "uuid": extracted_uuid,
            "content_type": "text"
        }
    
    def detect_image(self, image_path: str) -> Dict:
        """
        Detect watermark in image.
        
        Args:
            image_path: Image path to check
            
        Returns:
            Detection result dictionary
        """
        if not self.image_processor:
            raise ValueError("Image processing not available")
        
        image = self.image_processor.load_image(image_path)
        extracted_uuid = self.image_watermarker.extract(image, strength=self.watermark_strength)
        
        return {
            "detected": extracted_uuid is not None,
            "uuid": extracted_uuid,
            "content_type": "image"
        }
