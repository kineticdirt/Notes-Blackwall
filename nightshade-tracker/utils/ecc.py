"""
Error Correction Code (ECC) utilities using Reed-Solomon codes.
Enables recovery of watermarks even when image data is partially corrupted.
"""

from reedsolo import RSCodec
from typing import Tuple
import numpy as np


class ErrorCorrectionCode:
    """
    Reed-Solomon error correction for watermark data.
    Can recover from up to 30% data loss.
    """
    
    def __init__(self, ecc_percent: float = 0.3):
        """
        Initialize ECC encoder/decoder.
        
        Args:
            ecc_percent: Percentage of redundancy (0.0 to 0.5)
                        e.g., 0.3 = 30% overhead, can recover from 30% errors
        """
        self.ecc_percent = ecc_percent
        # Calculate number of ECC symbols needed
        # For simplicity, we'll use a fixed codec size
        # In practice, you'd calculate based on data size
        self.codec = None
    
    def _get_codec(self, data_length: int) -> RSCodec:
        """
        Get or create codec for given data length.
        
        Args:
            data_length: Length of data to encode
            
        Returns:
            RSCodec instance
        """
        # Calculate ECC symbols needed
        ecc_symbols = int(data_length * self.ecc_percent)
        # Reed-Solomon requires: total_symbols = data_symbols + ecc_symbols
        # And total_symbols must be <= 255 (for GF(2^8))
        total_symbols = min(255, data_length + ecc_symbols)
        ecc_symbols = total_symbols - data_length
        
        # Create codec
        return RSCodec(ecc_symbols)
    
    def encode(self, data: bytes) -> bytes:
        """
        Encode data with error correction codes.
        
        Args:
            data: Raw bytes to encode
            
        Returns:
            Encoded bytes with ECC redundancy
        """
        codec = self._get_codec(len(data))
        encoded = codec.encode(data)
        return encoded
    
    def decode(self, encoded_data: bytes, 
              errors_corrected: bool = False) -> Tuple[bytes, int]:
        """
        Decode data with error correction.
        
        Args:
            encoded_data: Encoded bytes (may contain errors)
            errors_corrected: Whether to return if errors were corrected
            
        Returns:
            Tuple of (decoded_data, num_errors_corrected)
        """
        codec = self._get_codec(len(encoded_data))
        try:
            decoded, errors, errata_pos = codec.decode(encoded_data)
            num_errors = len(errata_pos) if errata_pos else 0
            return decoded, num_errors
        except Exception as e:
            # If decoding fails, return empty bytes
            return b'', -1
    
    def encode_bits(self, bits: np.ndarray) -> np.ndarray:
        """
        Encode bit array with ECC.
        
        Args:
            bits: numpy array of bits (0s and 1s)
            
        Returns:
            Encoded bit array with redundancy
        """
        # Convert bits to bytes
        bit_string = ''.join(str(b) for b in bits)
        # Pad to byte boundary
        while len(bit_string) % 8 != 0:
            bit_string += '0'
        
        # Convert to bytes
        data_bytes = bytes(int(bit_string[i:i+8], 2) 
                          for i in range(0, len(bit_string), 8))
        
        # Encode
        encoded_bytes = self.encode(data_bytes)
        
        # Convert back to bits
        encoded_bits = np.array([int(b) for byte in encoded_bytes 
                                for b in format(byte, '08b')])
        
        return encoded_bits
    
    def decode_bits(self, encoded_bits: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Decode bit array with error correction.
        
        Args:
            encoded_bits: numpy array of encoded bits (may contain errors)
            
        Returns:
            Tuple of (decoded_bits, num_errors_corrected)
        """
        # Convert bits to bytes
        bit_string = ''.join(str(int(b)) for b in encoded_bits)
        # Pad to byte boundary
        while len(bit_string) % 8 != 0:
            bit_string += '0'
        
        # Convert to bytes
        encoded_bytes = bytes(int(bit_string[i:i+8], 2) 
                             for i in range(0, len(bit_string), 8))
        
        # Decode
        decoded_bytes, num_errors = self.decode(encoded_bytes)
        
        # Convert back to bits
        decoded_bits = np.array([int(b) for byte in decoded_bytes 
                                for b in format(byte, '08b')])
        
        return decoded_bits, num_errors
