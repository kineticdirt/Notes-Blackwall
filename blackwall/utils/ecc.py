"""
Error Correction Code utilities (shared from nightshade-tracker).
"""

import sys
from pathlib import Path

# Import from nightshade-tracker if available
nightshade_path = Path(__file__).parent.parent.parent / "nightshade-tracker"
if nightshade_path.exists():
    sys.path.insert(0, str(nightshade_path))
    from utils.ecc import ErrorCorrectionCode
else:
    # Fallback implementation
    from reedsolo import RSCodec
    from typing import Tuple
    import numpy as np
    
    class ErrorCorrectionCode:
        def __init__(self, ecc_percent: float = 0.3):
            self.ecc_percent = ecc_percent
        
        def _get_codec(self, data_length: int) -> RSCodec:
            ecc_symbols = int(data_length * self.ecc_percent)
            total_symbols = min(255, data_length + ecc_symbols)
            ecc_symbols = total_symbols - data_length
            return RSCodec(ecc_symbols)
        
        def encode(self, data: bytes) -> bytes:
            codec = self._get_codec(len(data))
            return codec.encode(data)
        
        def decode(self, encoded_data: bytes) -> Tuple[bytes, int]:
            codec = self._get_codec(len(encoded_data))
            try:
                decoded, errors, errata_pos = codec.decode(encoded_data)
                return decoded, len(errata_pos) if errata_pos else 0
            except:
                return b'', -1
