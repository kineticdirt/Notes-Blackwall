"""
Robust watermarking/steganography module.
Embeds UUIDs into images using frequency-domain techniques that survive compression.
"""

import numpy as np
import uuid
from typing import Tuple, Optional
import cv2

from utils.ecc import ErrorCorrectionCode


class RobustWatermarker:
    """
    Embeds and extracts robust watermarks using frequency-domain steganography.
    Uses DCT (Discrete Cosine Transform) for JPEG-compatible embedding.
    """
    
    def __init__(self, uuid_bits: int = 256, redundancy_factor: int = 15,
                 ecc_enabled: bool = True, ecc_redundancy: float = 0.3):
        """
        Initialize watermarker.
        
        Args:
            uuid_bits: Size of UUID in bits (128 or 256)
            redundancy_factor: Number of times to embed UUID
            ecc_enabled: Enable error correction codes
            ecc_redundancy: ECC redundancy percentage
        """
        self.uuid_bits = uuid_bits
        self.redundancy_factor = redundancy_factor
        self.ecc_enabled = ecc_enabled
        self.ecc = ErrorCorrectionCode(ecc_redundancy) if ecc_enabled else None
        
        # Generate UUID
        self.uuid = self._generate_uuid()
        self.uuid_binary = self._uuid_to_binary(self.uuid)
    
    def _generate_uuid(self) -> str:
        """Generate a UUID string."""
        return str(uuid.uuid4())
    
    def _uuid_to_binary(self, uuid_str: str) -> np.ndarray:
        """
        Convert UUID string to binary array.
        
        Args:
            uuid_str: UUID string
            
        Returns:
            numpy array of bits
        """
        # Remove hyphens and convert hex to binary
        hex_str = uuid_str.replace('-', '')
        binary_str = ''.join(format(int(c, 16), '04b') for c in hex_str)
        bits = np.array([int(b) for b in binary_str])
        
        # Truncate or pad to desired length
        if len(bits) > self.uuid_bits:
            bits = bits[:self.uuid_bits]
        elif len(bits) < self.uuid_bits:
            # Pad with zeros
            padding = np.zeros(self.uuid_bits - len(bits), dtype=int)
            bits = np.concatenate([bits, padding])
        
        return bits
    
    def _binary_to_uuid(self, bits: np.ndarray) -> Optional[str]:
        """
        Convert binary array back to UUID string.
        
        Args:
            bits: numpy array of bits
            
        Returns:
            UUID string or None if invalid
        """
        try:
            # Convert bits to hex
            bit_string = ''.join(str(int(b)) for b in bits)
            # Pad to hex boundary
            while len(bit_string) % 4 != 0:
                bit_string += '0'
            
            # Convert to hex string
            hex_str = ''.join(hex(int(bit_string[i:i+4], 2))[2:] 
                            for i in range(0, len(bit_string), 4))
            
            # Format as UUID (32 hex chars)
            if len(hex_str) >= 32:
                hex_str = hex_str[:32]
                uuid_str = f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
                return uuid_str
        except Exception:
            pass
        return None
    
    def embed(self, image: np.ndarray, strength: float = 0.01) -> np.ndarray:
        """
        Embed watermark into image using DCT-based steganography.
        
        Args:
            image: Input image array (H, W, C) in RGB
            strength: Embedding strength (0.0 to 1.0)
            
        Returns:
            Watermarked image array
        """
        watermarked = image.copy().astype(np.float32)
        h, w, c = image.shape
        
        # Prepare payload with redundancy
        payload = self.uuid_binary.copy()
        
        # Add error correction if enabled
        if self.ecc_enabled:
            payload = self.ecc.encode_bits(payload)
        
        # Repeat payload for redundancy
        full_payload = np.tile(payload, self.redundancy_factor)
        
        # Embed in Y channel (luminance) - most robust
        # Convert to YUV
        yuv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
        
        # Divide into 8x8 blocks (JPEG-style)
        block_size = 8
        payload_idx = 0
        
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                if payload_idx >= len(full_payload):
                    break
                
                # Extract block
                block = y_channel[i:i+block_size, j:j+block_size]
                
                # Apply DCT
                dct_block = cv2.dct(block)
                
                # Embed bit in mid-frequency coefficient (robust to compression)
                # Use (3, 4) or (4, 3) position (avoiding DC and high frequencies)
                bit = full_payload[payload_idx]
                
                # Quantize coefficient to embed bit
                coeff = dct_block[3, 4]
                if bit == 1:
                    # Set to odd quantized value
                    quantized = np.round(coeff / strength) * strength
                    if int(quantized / strength) % 2 == 0:
                        quantized += strength
                else:
                    # Set to even quantized value
                    quantized = np.round(coeff / strength) * strength
                    if int(quantized / strength) % 2 == 1:
                        quantized -= strength
                
                dct_block[3, 4] = quantized
                
                # Inverse DCT
                modified_block = cv2.idct(dct_block)
                
                # Update Y channel
                y_channel[i:i+block_size, j:j+block_size] = modified_block
                
                payload_idx += 1
        
        # Convert back to RGB
        yuv[:, :, 0] = np.clip(y_channel, 0, 255).astype(np.uint8)
        watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
        
        return watermarked.astype(np.uint8)
    
    def extract(self, image: np.ndarray, strength: float = 0.01) -> Optional[str]:
        """
        Extract watermark from image.
        
        Args:
            image: Image array (may be compressed/modified)
            strength: Embedding strength used (should match embed)
            
        Returns:
            Extracted UUID string or None if not found
        """
        # Convert to YUV and extract Y channel
        yuv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2YUV)
        y_channel = yuv[:, :, 0].astype(np.float32)
        
        h, w = y_channel.shape
        block_size = 8
        
        extracted_bits = []
        
        # Extract from all blocks
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                # Extract block
                block = y_channel[i:i+block_size, j:j+block_size]
                
                # Apply DCT
                dct_block = cv2.dct(block)
                
                # Extract bit from mid-frequency coefficient
                coeff = dct_block[3, 4]
                quantized = np.round(coeff / strength)
                bit = int(quantized) % 2
                
                extracted_bits.append(bit)
        
        if len(extracted_bits) == 0:
            return None
        
        # Convert to numpy array
        extracted_bits = np.array(extracted_bits)
        
        # Determine payload size (with ECC if enabled)
        payload_size = len(self.uuid_binary)
        if self.ecc_enabled:
            payload_size = len(self.ecc.encode_bits(self.uuid_binary))
        
        # Extract payloads (with redundancy)
        payloads = []
        for i in range(0, len(extracted_bits), payload_size):
            if i + payload_size <= len(extracted_bits):
                payload = extracted_bits[i:i+payload_size]
                payloads.append(payload)
        
        # Decode with majority voting
        decoded_payloads = []
        for payload in payloads:
            if self.ecc_enabled:
                decoded, errors = self.ecc.decode_bits(payload)
                if errors >= 0:  # Valid decode
                    decoded_payloads.append(decoded[:len(self.uuid_binary)])
            else:
                decoded_payloads.append(payload[:len(self.uuid_binary)])
        
        if len(decoded_payloads) == 0:
            return None
        
        # Majority voting on each bit
        if len(decoded_payloads) > 0:
            stacked = np.stack(decoded_payloads)
            majority_bits = (np.sum(stacked, axis=0) > len(stacked) / 2).astype(int)
            
            # Convert to UUID
            uuid_str = self._binary_to_uuid(majority_bits)
            return uuid_str
        
        return None
    
    def get_uuid(self) -> str:
        """Get the current UUID."""
        return self.uuid
