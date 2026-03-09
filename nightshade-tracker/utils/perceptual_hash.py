"""
Perceptual hashing utilities for image fingerprinting.
Generates robust hashes that survive compression and minor modifications.
"""

import imagehash
import numpy as np
from PIL import Image
from typing import Union


def compute_phash(image: Union[np.ndarray, Image.Image], 
                 hash_size: int = 16) -> str:
    """
    Compute perceptual hash (pHash) of an image.
    pHash is robust to compression, resizing, and minor modifications.
    
    Args:
        image: numpy array or PIL Image
        hash_size: Size of hash (8, 16, 32, 64). Larger = more robust but slower
        
    Returns:
        Hexadecimal hash string
    """
    if isinstance(image, np.ndarray):
        # Convert numpy array to PIL Image
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        pil_image = Image.fromarray(image)
    else:
        pil_image = image
    
    # Compute perceptual hash
    phash = imagehash.phash(pil_image, hash_size=hash_size)
    return str(phash)


def compute_multiple_hashes(image: Union[np.ndarray, Image.Image]) -> dict:
    """
    Compute multiple hash types for robust matching.
    
    Args:
        image: numpy array or PIL Image
        
    Returns:
        Dictionary with different hash types
    """
    if isinstance(image, np.ndarray):
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        pil_image = Image.fromarray(image)
    else:
        pil_image = image
    
    return {
        'phash': str(imagehash.phash(pil_image, hash_size=16)),
        'phash_large': str(imagehash.phash(pil_image, hash_size=32)),
        'dhash': str(imagehash.dhash(pil_image, hash_size=16)),
        'whash': str(imagehash.whash(pil_image, hash_size=16)),
    }


def hash_distance(hash1: str, hash2: str) -> int:
    """
    Compute Hamming distance between two hashes.
    Lower distance = more similar images.
    
    Args:
        hash1, hash2: Hexadecimal hash strings
        
    Returns:
        Hamming distance (0 = identical, higher = more different)
    """
    h1 = imagehash.hex_to_hash(hash1)
    h2 = imagehash.hex_to_hash(hash2)
    return h1 - h2


def is_match(hash1: str, hash2: str, threshold: int = 5) -> bool:
    """
    Check if two hashes match within threshold.
    
    Args:
        hash1, hash2: Hexadecimal hash strings
        threshold: Maximum Hamming distance for a match
        
    Returns:
        True if hashes match within threshold
    """
    distance = hash_distance(hash1, hash2)
    return distance <= threshold
