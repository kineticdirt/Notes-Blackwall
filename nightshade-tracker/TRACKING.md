# Tracking & Usage Trail Documentation

## Overview

The Nightshade Tracker system is designed to **track where your images are being used** by building a complete usage trail. When you process an image, it gets a unique UUID watermark. When that image is detected anywhere (datasets, websites, APIs), the system logs where it was found.

## Key Features

### 1. Enhanced Detection Logging

Every time a watermarked image is detected, the system logs:
- **Source Path**: Where the image was found
- **Source URL**: Web URL (if applicable)
- **Source Dataset**: Dataset name (e.g., "LAION-5B", "HuggingFace")
- **Source Type**: Type of source ("web", "dataset", "local", "api")
- **Context Metadata**: Additional information (API responses, headers, etc.)
- **Image Metadata**: Size, dimensions, format of detected image
- **Confidence**: How confident the match is

### 2. Usage Trail

For each tracked image, you can see:
- **All detection locations**: Complete list of where the image was found
- **Dataset statistics**: Which datasets contain your image
- **Source type breakdown**: Web, datasets, APIs, etc.
- **Timeline**: First and last detection times

### 3. Tracking Summary

Get overall statistics:
- Total images tracked
- Total detections across all images
- Unique datasets found
- Detections by source type
- Detections by dataset

## Usage Examples

### Track an Image

```bash
# Process and register an image
python cli.py process -i my_art.jpg -o my_art_tracked.jpg
```

### Scan a Dataset

```bash
# Scan a dataset and track where images are found
python cli.py scan -d /path/to/laion-dataset \
  --dataset-name "LAION-5B" \
  --source-type "dataset" \
  -o matches.json
```

### View Usage Trail

```bash
# See complete usage trail for an image
python cli.py trail --id 1

# Save trail to file
python cli.py trail --id 1 -o trail.json
```

### Get Tracking Summary

```bash
# See overall tracking statistics
python cli.py summary

# Save summary to file
python cli.py summary -o summary.json
```

### List All Detections

```bash
# List all detections
python cli.py detections

# Filter by image ID
python cli.py detections --id 1

# Filter by dataset
python cli.py detections --dataset "LAION-5B"

# Filter by source type
python cli.py detections --source-type "web"
```

## Python API

### Enhanced Detection with Tracking

```python
from core.detector import WatermarkDetector
from database.registry import ImageRegistry

registry = ImageRegistry()
detector = WatermarkDetector(registry)

# Detect with tracking info
result = detector.detect(
    "suspicious_image.jpg",
    source_url="https://example.com/image.jpg",
    source_dataset="LAION-5B",
    source_type="dataset",
    context_metadata={
        "crawler": "laion-crawler",
        "timestamp": "2025-01-15T10:30:00Z"
    }
)
```

### Get Usage Trail

```python
from database.registry import ImageRegistry

registry = ImageRegistry()

# Get complete trail for image ID 1
trail = registry.get_usage_trail(1)

print(f"Total detections: {trail['total_detections']}")
print(f"Found in datasets: {trail['datasets']}")
print(f"Found in sources: {trail['sources']}")

# List all detections
for det in trail['detections']:
    print(f"Found at: {det['source_path']}")
    print(f"  Dataset: {det.get('source_dataset')}")
    print(f"  URL: {det.get('source_url')}")
```

### Get Tracking Summary

```python
from database.registry import ImageRegistry

registry = ImageRegistry()
summary = registry.get_tracking_summary()

print(f"Total images tracked: {summary['total_images_tracked']}")
print(f"Total detections: {summary['total_detections']}")
print(f"Unique datasets: {summary['unique_datasets']}")
print(f"Detections by dataset: {summary['detections_by_dataset']}")
```

## Database Schema

### Images Table
Stores all registered images with their UUIDs and hashes.

### Detections Table
Stores every detection event with:
- `image_id`: Reference to registered image
- `source_path`: Where image was found
- `source_url`: Web URL (if applicable)
- `source_dataset`: Dataset name
- `source_type`: Type of source
- `confidence`: Match confidence
- `context_metadata`: Additional context (JSON)
- `detected_at`: Timestamp

## Use Cases

### 1. Track Dataset Usage
```bash
# Scan LAION dataset
python cli.py scan -d /data/laion --dataset-name "LAION-5B" --source-type "dataset"
```

### 2. Track Web Usage
When scanning web sources, include URLs:
```python
detector.detect(
    image_path,
    source_url="https://example.com/image.jpg",
    source_type="web"
)
```

### 3. Track API Usage
When images are found via APIs:
```python
detector.detect(
    image_path,
    source_url="https://api.example.com/v1/images/123",
    source_type="api",
    context_metadata={
        "api_key": "masked",
        "response_code": 200
    }
)
```

## Building a Complete Trail

The system builds a complete trail by:
1. **Registering** images with UUID + pHash
2. **Detecting** watermarks in external sources
3. **Logging** every detection with full context
4. **Aggregating** statistics for reporting

This gives you a complete audit trail of where your images are being used, which is valuable for:
- Understanding image distribution
- Identifying unauthorized usage
- Tracking dataset inclusion
- Building evidence for legal cases
