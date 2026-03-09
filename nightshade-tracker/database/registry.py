"""
Database registry for tracking processed images and text.
Stores UUID, perceptual hash, and metadata for legal proof.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import os
from pathlib import Path


class ImageRegistry:
    """
    SQLite-based registry for tracking processed images.
    Stores UUID, pHash, and metadata for detection and legal proof.
    """
    
    def __init__(self, db_path: str = "registry.db"):
        """
        Initialize registry database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create main registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                processed_filename TEXT,
                uuid TEXT NOT NULL UNIQUE,
                phash TEXT NOT NULL,
                phash_large TEXT,
                dhash TEXT,
                whash TEXT,
                file_path TEXT,
                file_size INTEGER,
                image_width INTEGER,
                image_height INTEGER,
                format TEXT,
                poison_strength REAL,
                watermark_strength REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Create index for fast UUID lookup
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_uuid ON images(uuid)
        ''')
        
        # Create index for pHash lookup (for similarity search)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_phash ON images(phash)
        ''')
        
        # Create detection log table (enhanced for tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                detected_uuid TEXT,
                detected_phash TEXT,
                source_path TEXT,
                source_url TEXT,
                source_dataset TEXT,
                source_type TEXT,
                confidence REAL,
                file_size INTEGER,
                image_width INTEGER,
                image_height INTEGER,
                format TEXT,
                context_metadata TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (image_id) REFERENCES images(id)
            )
        ''')
        
        # Create index for tracking queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_detections_image_id ON detections(image_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_detections_source ON detections(source_dataset, source_type)
        ''')
        
        # Create text registry table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                processed_filename TEXT,
                uuid TEXT NOT NULL UNIQUE,
                text_hash TEXT NOT NULL,
                file_path TEXT,
                file_size INTEGER,
                word_count INTEGER,
                char_count INTEGER,
                line_count INTEGER,
                format TEXT,
                poison_strength REAL,
                watermark_strength REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Create index for text UUID lookup
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_text_uuid ON text_files(uuid)
        ''')
        
        # Create text detection log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS text_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_id INTEGER,
                detected_uuid TEXT,
                detected_hash TEXT,
                source_path TEXT,
                source_url TEXT,
                source_dataset TEXT,
                source_type TEXT,
                confidence REAL,
                file_size INTEGER,
                word_count INTEGER,
                char_count INTEGER,
                format TEXT,
                context_metadata TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (text_id) REFERENCES text_files(id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_text_detections_text_id ON text_detections(text_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def register_image(self, original_filename: str, uuid: str, phash: str,
                      processed_filename: Optional[str] = None,
                      phash_large: Optional[str] = None,
                      dhash: Optional[str] = None,
                      whash: Optional[str] = None,
                      file_path: Optional[str] = None,
                      file_size: Optional[int] = None,
                      image_width: Optional[int] = None,
                      image_height: Optional[int] = None,
                      format: Optional[str] = None,
                      poison_strength: Optional[float] = None,
                      watermark_strength: Optional[float] = None,
                      metadata: Optional[Dict] = None) -> int:
        """
        Register a processed image in the database.
        
        Args:
            original_filename: Original filename
            uuid: UUID embedded in image
            phash: Perceptual hash
            processed_filename: Processed filename (optional)
            phash_large: Large perceptual hash (optional)
            dhash: Difference hash (optional)
            whash: Wavelet hash (optional)
            file_path: Full file path (optional)
            file_size: File size in bytes (optional)
            image_width: Image width (optional)
            image_height: Image height (optional)
            format: Image format (optional)
            poison_strength: Poison strength used (optional)
            watermark_strength: Watermark strength used (optional)
            metadata: Additional metadata dict (optional)
            
        Returns:
            Database ID of registered image
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO images (
                original_filename, processed_filename, uuid, phash,
                phash_large, dhash, whash, file_path, file_size,
                image_width, image_height, format, poison_strength,
                watermark_strength, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            original_filename, processed_filename, uuid, phash,
            phash_large, dhash, whash, file_path, file_size,
            image_width, image_height, format, poison_strength,
            watermark_strength, metadata_json
        ))
        
        image_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return image_id
    
    def lookup_by_uuid(self, uuid: str) -> Optional[Dict]:
        """
        Look up image by UUID.
        
        Args:
            uuid: UUID to search for
            
        Returns:
            Dictionary with image info or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM images WHERE uuid = ?
        ''', (uuid,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        # Convert to dict
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        # Parse metadata JSON
        if result.get('metadata'):
            result['metadata'] = json.loads(result['metadata'])
        
        return result
    
    def lookup_by_phash(self, phash: str, threshold: int = 5) -> List[Dict]:
        """
        Look up images by perceptual hash (similarity search).
        
        Args:
            phash: Perceptual hash to search for
            threshold: Maximum Hamming distance for match
            
        Returns:
            List of matching images
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all images (for now, simple approach)
        # In production, use more efficient similarity search
        cursor.execute('SELECT * FROM images')
        all_rows = cursor.fetchall()
        conn.close()
        
        # Compute distances and filter
        from utils.perceptual_hash import hash_distance
        
        matches = []
        columns = [desc[0] for desc in cursor.description]
        
        for row in all_rows:
            result = dict(zip(columns, row))
            stored_phash = result.get('phash')
            
            if stored_phash:
                distance = hash_distance(phash, stored_phash)
                if distance <= threshold:
                    result['phash_distance'] = distance
                    if result.get('metadata'):
                        result['metadata'] = json.loads(result['metadata'])
                    matches.append(result)
        
        # Sort by distance
        matches.sort(key=lambda x: x.get('phash_distance', float('inf')))
        
        return matches
    
    def log_detection(self, image_id: int, detected_uuid: str,
                     detected_phash: str, source_path: str,
                     confidence: float,
                     source_url: Optional[str] = None,
                     source_dataset: Optional[str] = None,
                     source_type: Optional[str] = None,
                     file_size: Optional[int] = None,
                     image_width: Optional[int] = None,
                     image_height: Optional[int] = None,
                     format: Optional[str] = None,
                     context_metadata: Optional[Dict] = None) -> int:
        """
        Log a detection event (when watermark is found in external image).
        Enhanced for tracking usage trails.
        
        Args:
            image_id: ID of registered image
            detected_uuid: UUID extracted from detected image
            detected_phash: pHash of detected image
            source_path: Path where image was detected
            confidence: Confidence score (0.0 to 1.0)
            source_url: URL where image was found (if web source)
            source_dataset: Dataset name (e.g., "LAION-5B", "HuggingFace")
            source_type: Type of source ("web", "dataset", "local", "api")
            file_size: File size of detected image
            image_width: Width of detected image
            image_height: Height of detected image
            format: Format of detected image
            context_metadata: Additional context (e.g., API response, headers)
            
        Returns:
            Detection log ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context_json = json.dumps(context_metadata) if context_metadata else None
        
        cursor.execute('''
            INSERT INTO detections (
                image_id, detected_uuid, detected_phash,
                source_path, source_url, source_dataset, source_type,
                confidence, file_size, image_width, image_height,
                format, context_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_id, detected_uuid, detected_phash,
            source_path, source_url, source_dataset, source_type,
            confidence, file_size, image_width, image_height,
            format, context_json
        ))
        
        detection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return detection_id
    
    def get_detections(self, image_id: Optional[int] = None,
                     source_dataset: Optional[str] = None,
                     source_type: Optional[str] = None) -> List[Dict]:
        """
        Get detection logs with filtering options.
        
        Args:
            image_id: Filter by image ID (None = all detections)
            source_dataset: Filter by dataset name
            source_type: Filter by source type
            
        Returns:
            List of detection records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM detections WHERE 1=1'
        params = []
        
        if image_id:
            query += ' AND image_id = ?'
            params.append(image_id)
        if source_dataset:
            query += ' AND source_dataset = ?'
            params.append(source_dataset)
        if source_type:
            query += ' AND source_type = ?'
            params.append(source_type)
        
        query += ' ORDER BY detected_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('context_metadata'):
                result['context_metadata'] = json.loads(result['context_metadata'])
            results.append(result)
        
        return results
    
    def lookup_by_id(self, image_id: int) -> Optional[Dict]:
        """
        Look up image by database ID.
        
        Args:
            image_id: Database ID
            
        Returns:
            Dictionary with image info or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM images WHERE id = ?
        ''', (image_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        # Convert to dict
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        # Parse metadata JSON
        if result.get('metadata'):
            result['metadata'] = json.loads(result['metadata'])
        
        return result
    
    def get_usage_trail(self, image_id: int) -> Dict:
        """
        Get complete usage trail for an image.
        
        Args:
            image_id: ID of registered image
            
        Returns:
            Dictionary with image info and all detections
        """
        image = self.lookup_by_id(image_id)
        
        if not image:
            return {'error': 'Image not found'}
        
        detections = self.get_detections(image_id=image_id)
        
        # Aggregate statistics
        datasets = {}
        sources = {}
        for det in detections:
            dataset = det.get('source_dataset', 'unknown')
            source_type = det.get('source_type', 'unknown')
            datasets[dataset] = datasets.get(dataset, 0) + 1
            sources[source_type] = sources.get(source_type, 0) + 1
        
        return {
            'image': image,
            'detections': detections,
            'total_detections': len(detections),
            'datasets': datasets,
            'sources': sources,
            'first_detected': detections[-1]['detected_at'] if detections else None,
            'last_detected': detections[0]['detected_at'] if detections else None
        }
    
    def get_tracking_summary(self) -> Dict:
        """
        Get summary of all tracking activity.
        
        Returns:
            Dictionary with tracking statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total images tracked
        cursor.execute('SELECT COUNT(*) FROM images')
        total_images = cursor.fetchone()[0]
        
        # Total detections
        cursor.execute('SELECT COUNT(*) FROM detections')
        total_detections = cursor.fetchone()[0]
        
        # Unique datasets
        cursor.execute('SELECT DISTINCT source_dataset FROM detections WHERE source_dataset IS NOT NULL')
        datasets = [row[0] for row in cursor.fetchall()]
        
        # Detections by source type
        cursor.execute('''
            SELECT source_type, COUNT(*) as count
            FROM detections
            WHERE source_type IS NOT NULL
            GROUP BY source_type
        ''')
        source_types = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Detections by dataset
        cursor.execute('''
            SELECT source_dataset, COUNT(*) as count
            FROM detections
            WHERE source_dataset IS NOT NULL
            GROUP BY source_dataset
            ORDER BY count DESC
        ''')
        dataset_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_images_tracked': total_images,
            'total_detections': total_detections,
            'unique_datasets': len(datasets),
            'datasets': datasets,
            'detections_by_source_type': source_types,
            'detections_by_dataset': dataset_counts
        }
    
    def get_all_images(self) -> List[Dict]:
        """Get all registered images."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM images ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            results.append(result)
        
        return results
    
    def backup(self, backup_path: Optional[str] = None):
        """
        Backup database.
        
        Args:
            backup_path: Path for backup file (None = auto-generate)
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"registry_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def register_text(self, original_filename: str, uuid: str, text_hash: str,
                     processed_filename: Optional[str] = None,
                     file_path: Optional[str] = None,
                     file_size: Optional[int] = None,
                     word_count: Optional[int] = None,
                     char_count: Optional[int] = None,
                     line_count: Optional[int] = None,
                     format: Optional[str] = None,
                     poison_strength: Optional[float] = None,
                     watermark_strength: Optional[float] = None,
                     metadata: Optional[Dict] = None) -> int:
        """
        Register a processed text file in the database.
        
        Args:
            original_filename: Original filename
            uuid: UUID embedded in text
            text_hash: Hash of text content
            processed_filename: Processed filename (optional)
            file_path: Full file path (optional)
            file_size: File size in bytes (optional)
            word_count: Word count (optional)
            char_count: Character count (optional)
            line_count: Line count (optional)
            format: Text format (optional)
            poison_strength: Poison strength used (optional)
            watermark_strength: Watermark strength used (optional)
            metadata: Additional metadata dict (optional)
            
        Returns:
            Database ID of registered text file
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO text_files (
                original_filename, processed_filename, uuid, text_hash,
                file_path, file_size, word_count, char_count, line_count,
                format, poison_strength, watermark_strength, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            original_filename, processed_filename, uuid, text_hash,
            file_path, file_size, word_count, char_count, line_count,
            format, poison_strength, watermark_strength, metadata_json
        ))
        
        text_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return text_id
    
    def lookup_text_by_uuid(self, uuid: str) -> Optional[Dict]:
        """
        Look up text file by UUID.
        
        Args:
            uuid: UUID to search for
            
        Returns:
            Dictionary with text file info or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM text_files WHERE uuid = ?
        ''', (uuid,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        if result.get('metadata'):
            result['metadata'] = json.loads(result['metadata'])
        
        return result
    
    def log_text_detection(self, text_id: int, detected_uuid: str,
                          detected_hash: str, source_path: str,
                          confidence: float,
                          source_url: Optional[str] = None,
                          source_dataset: Optional[str] = None,
                          source_type: Optional[str] = None,
                          file_size: Optional[int] = None,
                          word_count: Optional[int] = None,
                          char_count: Optional[int] = None,
                          format: Optional[str] = None,
                          context_metadata: Optional[Dict] = None) -> int:
        """
        Log a text detection event.
        
        Args:
            text_id: ID of registered text file
            detected_uuid: UUID extracted from detected text
            detected_hash: Hash of detected text
            source_path: Path where text was detected
            confidence: Confidence score (0.0 to 1.0)
            source_url: URL where text was found (if web source)
            source_dataset: Dataset name
            source_type: Type of source ("web", "dataset", "local", "api")
            file_size: File size of detected text
            word_count: Word count of detected text
            char_count: Character count of detected text
            format: Format of detected text
            context_metadata: Additional context
            
        Returns:
            Detection log ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context_json = json.dumps(context_metadata) if context_metadata else None
        
        cursor.execute('''
            INSERT INTO text_detections (
                text_id, detected_uuid, detected_hash,
                source_path, source_url, source_dataset, source_type,
                confidence, file_size, word_count, char_count,
                format, context_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            text_id, detected_uuid, detected_hash,
            source_path, source_url, source_dataset, source_type,
            confidence, file_size, word_count, char_count,
            format, context_json
        ))
        
        detection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return detection_id
    
    def get_all_text_files(self) -> List[Dict]:
        """Get all registered text files."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM text_files ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            results.append(result)
        
        return results
