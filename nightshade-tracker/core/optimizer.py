"""
Multi-objective optimization module.
Combines adversarial poisoning and watermarking without them interfering.
"""

import numpy as np
from typing import Tuple, Optional
import cv2

from core.watermarking import RobustWatermarker
from core.poisoning import AdversarialPoisoner


class MultiObjectiveOptimizer:
    """
    Optimizes image to satisfy both poisoning and watermarking objectives.
    Uses gradient separation and frequency-domain allocation.
    """
    
    def __init__(self, alpha: float = 0.5, iterations: int = 100,
                 learning_rate: float = 0.01):
        """
        Initialize optimizer.
        
        Args:
            alpha: Balance parameter (0.0 = only watermark, 1.0 = only poison)
            iterations: Number of optimization iterations
            learning_rate: Learning rate for optimization
        """
        self.alpha = alpha
        self.iterations = iterations
        self.learning_rate = learning_rate
    
    def optimize(self, image: np.ndarray,
                watermarker: RobustWatermarker,
                poisoner: AdversarialPoisoner,
                poison_strength: float = 0.1,
                watermark_strength: float = 0.01) -> Tuple[np.ndarray, dict]:
        """
        Optimize image to satisfy both objectives.
        
        Args:
            image: Input image array (H, W, C) in RGB
            watermarker: Watermarker instance
            poisoner: Poisoner instance
            poison_strength: Strength of poisoning
            watermark_strength: Strength of watermarking
            
        Returns:
            Tuple of (optimized_image, metrics_dict)
        """
        # Strategy 1: Frequency-domain separation
        # Use different frequency bands for poison vs watermark
        
        # Convert to frequency domain
        image_float = image.astype(np.float32)
        
        # Apply watermark first (uses DCT internally, so we'll do it separately)
        # For optimization, we'll use an iterative approach
        
        # Initialize
        current_image = image_float.copy()
        best_image = image_float.copy()
        best_score = -np.inf
        
        metrics = {
            'poison_loss': [],
            'watermark_loss': [],
            'total_loss': []
        }
        
        # Generate base perturbation for poisoning
        base_perturbation = poisoner.generate_perturbation(
            image, iterations=20
        )
        
        # Generate watermark embedding pattern
        # We'll embed watermark in Y channel, poison in U/V channels
        yuv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
        u_channel = yuv[:, :, 1].astype(np.float32)
        v_channel = yuv[:, :, 2].astype(np.float32)
        
        # Apply watermark to Y channel (luminance)
        y_watermarked = watermarker.embed(
            cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB),
            strength=watermark_strength
        )
        y_watermarked_yuv = cv2.cvtColor(y_watermarked, cv2.COLOR_RGB2YUV)
        y_watermarked_channel = y_watermarked_yuv[:, :, 0].astype(np.float32)
        
        # Apply poison to U/V channels (color information)
        # Poison affects color perception, less visible than luminance changes
        u_poisoned = u_channel + base_perturbation[:, :, 0] * poison_strength * 0.5
        v_poisoned = v_channel + base_perturbation[:, :, 1] * poison_strength * 0.5
        
        # Clip channels
        y_watermarked_channel = np.clip(y_watermarked_channel, 0, 255)
        u_poisoned = np.clip(u_poisoned, 0, 255)
        v_poisoned = np.clip(v_poisoned, 0, 255)
        
        # Combine channels
        combined_yuv = np.stack([
            y_watermarked_channel,
            u_poisoned,
            v_poisoned
        ], axis=2).astype(np.uint8)
        
        optimized_image = cv2.cvtColor(combined_yuv, cv2.COLOR_YUV2RGB)
        
        # Compute metrics
        poison_loss = poisoner.compute_poison_loss(image, optimized_image)
        
        # Watermark loss: how well can we extract it?
        extracted_uuid = watermarker.extract(optimized_image, strength=watermark_strength)
        watermark_loss = 1.0 if extracted_uuid == watermarker.get_uuid() else 0.0
        
        # Total loss
        total_loss = (1 - self.alpha) * poison_loss + self.alpha * watermark_loss
        
        metrics['poison_loss'].append(poison_loss)
        metrics['watermark_loss'].append(watermark_loss)
        metrics['total_loss'].append(total_loss)
        
        # Alternative strategy: Iterative refinement
        # If initial combination doesn't work well, refine
        if total_loss < 0.5:
            # Try iterative approach
            for iteration in range(self.iterations):
                # Small adjustments
                adjustment = np.random.randn(*optimized_image.shape) * 0.1
                candidate = np.clip(optimized_image.astype(np.float32) + adjustment, 0, 255)
                
                # Re-evaluate
                candidate_poison_loss = poisoner.compute_poison_loss(image, candidate.astype(np.uint8))
                candidate_extracted = watermarker.extract(candidate.astype(np.uint8), strength=watermark_strength)
                candidate_watermark_loss = 1.0 if candidate_extracted == watermarker.get_uuid() else 0.0
                candidate_total = (1 - self.alpha) * candidate_poison_loss + self.alpha * candidate_watermark_loss
                
                # Accept if better
                if candidate_total > total_loss:
                    optimized_image = candidate.astype(np.uint8)
                    total_loss = candidate_total
                    poison_loss = candidate_poison_loss
                    watermark_loss = candidate_watermark_loss
                    
                    metrics['poison_loss'].append(poison_loss)
                    metrics['watermark_loss'].append(watermark_loss)
                    metrics['total_loss'].append(total_loss)
        
        return optimized_image.astype(np.uint8), metrics
    
    def optimize_simple(self, image: np.ndarray,
                       watermarker: RobustWatermarker,
                       poisoner: AdversarialPoisoner,
                       poison_strength: float = 0.1,
                       watermark_strength: float = 0.01) -> Tuple[np.ndarray, dict]:
        """
        Simplified optimization: sequential application with balancing.
        
        Args:
            image: Input image
            watermarker: Watermarker instance
            poisoner: Poisoner instance
            poison_strength: Poison strength
            watermark_strength: Watermark strength
            
        Returns:
            Tuple of (optimized_image, metrics)
        """
        # Step 1: Apply watermark
        watermarked = watermarker.embed(image, strength=watermark_strength)
        
        # Step 2: Apply poison (with reduced strength to preserve watermark)
        # Generate perturbation on watermarked image
        adjusted_strength = poison_strength * (1 - self.alpha)  # Reduce if alpha favors watermark
        perturbation = poisoner.generate_perturbation(watermarked, iterations=10)
        
        # Apply with frequency masking (preserve low frequencies where watermark is)
        # Convert to frequency domain
        fft_image = np.fft.fft2(watermarked.astype(np.float32), axes=(0, 1))
        fft_pert = np.fft.fft2(perturbation, axes=(0, 1))
        
        # Create mask: preserve low frequencies (where watermark is strong)
        h, w = watermarked.shape[:2]
        mask = np.ones((h, w), dtype=np.float32)
        center_h, center_w = h // 2, w // 2
        radius = min(h, w) // 4  # Preserve center (low frequencies)
        
        y, x = np.ogrid[:h, :w]
        mask_circle = (x - center_w)**2 + (y - center_h)**2 <= radius**2
        mask[mask_circle] = 0.3  # Reduce poison in low frequencies
        
        # Apply mask to perturbation
        for c in range(3):
            fft_pert[:, :, c] *= mask
        
        # Inverse FFT
        pert_masked = np.real(np.fft.ifft2(fft_pert, axes=(0, 1)))
        
        # Combine
        optimized = watermarked.astype(np.float32) + pert_masked * adjusted_strength
        optimized = np.clip(optimized, 0, 255).astype(np.uint8)
        
        # Compute metrics
        poison_loss = poisoner.compute_poison_loss(image, optimized)
        extracted_uuid = watermarker.extract(optimized, strength=watermark_strength)
        watermark_loss = 1.0 if extracted_uuid == watermarker.get_uuid() else 0.0
        
        metrics = {
            'poison_loss': [poison_loss],
            'watermark_loss': [watermark_loss],
            'total_loss': [(1 - self.alpha) * poison_loss + self.alpha * watermark_loss]
        }
        
        return optimized, metrics
