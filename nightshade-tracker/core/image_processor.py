"""
Image processing module supporting JPG, PNG, and WebP formats.
Handles loading, conversion, and format-specific optimizations.
"""

import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional, Union
import io


class ImageProcessor:
    """Handles image loading, conversion, and format operations."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp'}
    
    def __init__(self):
        self.current_format = None
        self.original_image = None
    
    def load_image(self, path: str) -> np.ndarray:
        """
        Load image from file path, supporting JPG, PNG, and WebP.
        
        Args:
            path: Path to image file
            
        Returns:
            numpy array of image in RGB format (H, W, C)
        """
        # Detect format
        path_lower = path.lower()
        if any(path_lower.endswith(ext) for ext in ['.jpg', '.jpeg']):
            self.current_format = 'JPEG'
        elif path_lower.endswith('.png'):
            self.current_format = 'PNG'
        elif path_lower.endswith('.webp'):
            self.current_format = 'WEBP'
        else:
            raise ValueError(f"Unsupported format. Supported: {self.SUPPORTED_FORMATS}")
        
        # Load with PIL (handles all formats well)
        img = Image.open(path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        self.original_image = img
        return np.array(img)
    
    def save_image(self, image: np.ndarray, path: str, 
                   format: Optional[str] = None,
                   quality: int = 95) -> None:
        """
        Save image to file, preserving or converting format.
        
        Args:
            image: numpy array of image (H, W, C) in RGB
            path: Output file path
            format: Target format ('JPEG', 'PNG', 'WEBP'). If None, uses path extension
            quality: Quality for lossy formats (1-100)
        """
        # Determine format
        if format is None:
            path_lower = path.lower()
            if any(path_lower.endswith(ext) for ext in ['.jpg', '.jpeg']):
                format = 'JPEG'
            elif path_lower.endswith('.png'):
                format = 'PNG'
            elif path_lower.endswith('.webp'):
                format = 'WEBP'
            else:
                format = self.current_format or 'PNG'
        
        # Convert numpy array to PIL Image
        if image.dtype != np.uint8:
            # Clamp values to [0, 255] and convert
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        img = Image.fromarray(image)
        
        # Save with format-specific options
        save_kwargs = {}
        if format == 'JPEG':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif format == 'WEBP':
            save_kwargs['quality'] = quality
            save_kwargs['method'] = 6  # Best compression
        
        img.save(path, format=format, **save_kwargs)
    
    def get_image_info(self, image: np.ndarray) -> dict:
        """
        Get image metadata and statistics.
        
        Args:
            image: numpy array of image
            
        Returns:
            Dictionary with image info
        """
        h, w = image.shape[:2]
        return {
            'height': h,
            'width': w,
            'channels': image.shape[2] if len(image.shape) == 3 else 1,
            'dtype': str(image.dtype),
            'format': self.current_format,
            'size_bytes': image.nbytes
        }
    
    def resize_image(self, image: np.ndarray, 
                    target_size: Optional[Tuple[int, int]] = None,
                    max_dimension: Optional[int] = None) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: numpy array of image
            target_size: (width, height) tuple
            max_dimension: Maximum dimension (maintains aspect ratio)
            
        Returns:
            Resized image array
        """
        h, w = image.shape[:2]
        
        if target_size:
            new_w, new_h = target_size
        elif max_dimension:
            if w > h:
                new_w = max_dimension
                new_h = int(h * (max_dimension / w))
            else:
                new_h = max_dimension
                new_w = int(w * (max_dimension / h))
        else:
            return image
        
        # Use PIL for high-quality resizing
        img = Image.fromarray(image.astype(np.uint8))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        return np.array(img)
    
    def convert_to_yuv(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert RGB image to YUV color space.
        Useful for frequency-domain watermarking.
        
        Args:
            image: RGB image array
            
        Returns:
            Tuple of (Y, U, V) channels
        """
        yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        return yuv[:, :, 0], yuv[:, :, 1], yuv[:, :, 2]
    
    def convert_from_yuv(self, y: np.ndarray, u: np.ndarray, 
                        v: np.ndarray) -> np.ndarray:
        """
        Convert YUV channels back to RGB.
        
        Args:
            y, u, v: YUV channel arrays
            
        Returns:
            RGB image array
        """
        yuv = np.stack([y, u, v], axis=2)
        rgb = cv2.cvtColor(yuv.astype(np.uint8), cv2.COLOR_YUV2RGB)
        return rgb
