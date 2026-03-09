"""
Text processing module for handling text files.
Supports various text formats and operations.
"""

from typing import Optional, Dict
from pathlib import Path
import hashlib


class TextProcessor:
    """Handles text loading, saving, and format operations."""
    
    SUPPORTED_FORMATS = {'.txt', '.md', '.py', '.js', '.html', '.json', '.xml', '.csv'}
    
    def __init__(self):
        self.current_format = None
        self.original_text = None
    
    def load_text(self, path: str) -> str:
        """
        Load text from file path.
        
        Args:
            path: Path to text file
            
        Returns:
            Text content as string
        """
        # Detect format
        path_lower = path.lower()
        for ext in self.SUPPORTED_FORMATS:
            if path_lower.endswith(ext):
                self.current_format = ext[1:].upper()  # Remove dot
                break
        else:
            self.current_format = 'TXT'  # Default
        
        # Load text
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        self.original_text = text
        return text
    
    def save_text(self, text: str, path: str, 
                  format: Optional[str] = None) -> None:
        """
        Save text to file.
        
        Args:
            text: Text content
            path: Output file path
            format: Target format (optional, uses path extension)
        """
        # Determine format
        if format is None:
            path_lower = path.lower()
            for ext in self.SUPPORTED_FORMATS:
                if path_lower.endswith(ext):
                    format = ext[1:].upper()
                    break
            else:
                format = self.current_format or 'TXT'
        
        # Save text
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def get_text_info(self, text: str) -> Dict:
        """
        Get text metadata and statistics.
        
        Args:
            text: Text content
            
        Returns:
            Dictionary with text info
        """
        return {
            'length': len(text),
            'char_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.splitlines()),
            'format': self.current_format,
            'size_bytes': len(text.encode('utf-8')),
            'hash': hashlib.md5(text.encode('utf-8')).hexdigest()
        }
    
    def detect_encoding(self, path: str) -> str:
        """
        Detect text encoding.
        
        Args:
            path: Path to text file
            
        Returns:
            Detected encoding
        """
        try:
            import chardet
            with open(path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except ImportError:
            # Fallback to utf-8 if chardet not available
            return 'utf-8'
