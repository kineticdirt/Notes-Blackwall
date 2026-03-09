"""
Text watermarking/steganography module for Nightshade Tracker.
Embeds UUIDs into text using steganographic techniques.
"""

import uuid
import hashlib
from typing import Optional, List
import re
import numpy as np
from utils.ecc import ErrorCorrectionCode


class TextWatermarker:
    """
    Embeds and extracts robust watermarks in text.
    Uses invisible unicode characters that survive copy/paste.
    """
    
    def __init__(self, uuid_bits: int = 256, redundancy_factor: int = 10,
                 ecc_enabled: bool = True, ecc_redundancy: float = 0.3):
        """
        Initialize text watermarker.
        
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
    
    def _uuid_to_binary(self, uuid_str: str) -> List[int]:
        """Convert UUID string to binary list."""
        hex_str = uuid_str.replace('-', '')
        binary_str = ''.join(format(int(c, 16), '04b') for c in hex_str)
        bits = [int(b) for b in binary_str]
        
        # Truncate or pad to desired length
        if len(bits) > self.uuid_bits:
            bits = bits[:self.uuid_bits]
        elif len(bits) < self.uuid_bits:
            bits.extend([0] * (self.uuid_bits - len(bits)))
        
        return bits
    
    def _binary_to_uuid(self, bits: List[int]) -> Optional[str]:
        """Convert binary list back to UUID string."""
        try:
            bit_string = ''.join(str(b) for b in bits)
            # Pad to hex boundary
            while len(bit_string) % 4 != 0:
                bit_string += '0'
            
            # Convert to hex string
            hex_str = ''.join(hex(int(bit_string[i:i+4], 2))[2:] 
                            for i in range(0, len(bit_string), 4))
            
            # Format as UUID
            if len(hex_str) >= 32:
                hex_str = hex_str[:32]
                uuid_str = f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
                return uuid_str
        except Exception:
            pass
        return None
    
    def embed(self, text: str) -> str:
        """
        Embed watermark into text using invisible unicode.
        
        Args:
            text: Input text
            
        Returns:
            Watermarked text
        """
        # Prepare payload
        payload = self.uuid_binary.copy()
        
        if self.ecc_enabled:
            # Encode with ECC
            payload_bytes = bytes(int(''.join(str(b) for b in payload[i:i+8]), 2)
                                 for i in range(0, len(payload), 8))
            encoded = self.ecc.encode(payload_bytes)
            payload = [int(b) for byte in encoded 
                      for b in format(byte, '08b')]
        
        # Repeat for redundancy
        full_payload = (payload * self.redundancy_factor)[:len(text)]
        
        # Embed using zero-width characters
        # Zero-width space (U+200B) = 0
        # Zero-width non-joiner (U+200C) = 1
        watermarked = []
        payload_idx = 0
        
        for char in text:
            watermarked.append(char)
            # Insert watermark bit after each character
            if payload_idx < len(full_payload):
                if full_payload[payload_idx] == 1:
                    watermarked.append('\u200C')  # Zero-width non-joiner
                else:
                    watermarked.append('\u200B')  # Zero-width space
                payload_idx += 1
        
        return ''.join(watermarked)
    
    def extract(self, text: str) -> Optional[str]:
        """
        Extract watermark from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            Extracted UUID string or None
        """
        extracted_bits = []
        
        for char in text:
            if char == '\u200B':  # Zero-width space = 0
                extracted_bits.append(0)
            elif char == '\u200C':  # Zero-width non-joiner = 1
                extracted_bits.append(1)
        
        if len(extracted_bits) == 0:
            return None
        
        # Determine payload size
        payload_size = len(self.uuid_binary)
        if self.ecc_enabled:
            payload_size = len(self.ecc.encode(
                bytes(int(''.join(str(b) for b in self.uuid_binary[i:i+8]), 2)
                     for i in range(0, len(self.uuid_binary), 8))
            ))
        
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
                # Convert to bytes
                payload_bytes = bytes(int(''.join(str(b) for b in payload[i:i+8]), 2)
                                    for i in range(0, len(payload), 8))
                decoded, errors = self.ecc.decode(payload_bytes)
                if errors >= 0:
                    decoded_bits = [int(b) for byte in decoded 
                                  for b in format(byte, '08b')]
                    decoded_payloads.append(decoded_bits[:len(self.uuid_binary)])
            else:
                decoded_payloads.append(payload[:len(self.uuid_binary)])
        
        if len(decoded_payloads) == 0:
            return None
        
        # Majority voting
        if len(decoded_payloads) > 0:
            stacked = np.array(decoded_payloads)
            majority_bits = (np.sum(stacked, axis=0) > len(stacked) / 2).astype(int).tolist()
            
            # Convert to UUID
            uuid_str = self._binary_to_uuid(majority_bits)
            return uuid_str
        
        return None
    
    def get_uuid(self) -> str:
        """Get the current UUID."""
        return self.uuid
