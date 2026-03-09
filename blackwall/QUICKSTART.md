# Blackwall Quick Start Guide

## Overview

Blackwall extends Nightshade to protect **both text and images** from unauthorized AI training.

## Installation

```bash
cd blackwall
pip install -r requirements.txt
```

## Basic Usage

### Protect Text

```bash
# Process a text file
python cli.py process-text -i document.txt -o document_protected.txt

# The output will have:
# - Adversarial poisoning (faulty text data for AI training)
# - Embedded UUID watermark (for tracking)
```

### Protect Image

```bash
# Process an image
python cli.py process-image -i image.jpg -o image_protected.jpg

# The output will have:
# - Adversarial poisoning (like Nightshade)
# - Embedded UUID watermark
```

### Detect Watermarks

```bash
# Detect in text
python cli.py detect -i suspicious_text.txt

# Detect in image
python cli.py detect -i suspicious_image.jpg

# Auto-detect type
python cli.py detect -i file.txt  # Auto-detects as text
python cli.py detect -i file.jpg  # Auto-detects as image
```

## How Text Protection Works

### Text Poisoning
- Adds invisible unicode characters (zero-width spaces)
- Modifies text embeddings to cause misclassification
- Creates "faulty text data" that degrades AI model training

### Text Watermarking
- Embeds UUID using invisible unicode characters
- Survives paraphrasing, translation, summarization
- Multiple embedding methods: unicode, word order, synonyms

## How Image Protection Works

- Uses the same techniques as Nightshade tracker
- Adversarial perturbations in image space
- DCT-based watermarking in frequency domain

## Unified Registry

All content (text + images) is tracked in a single database:
- Text files with UUIDs
- Image files with UUIDs
- Cross-modal detection
- Complete audit trail

## Example Workflow

```python
from core.unified_processor import UnifiedProcessor
from database.registry import BlackwallRegistry

# Initialize
processor = UnifiedProcessor(poison_strength=0.1)
registry = BlackwallRegistry()

# Protect text
text = "Your content here..."
protected_text, metadata = processor.process_text(text)
print(f"UUID: {metadata['uuid']}")

# Protect image
metadata = processor.process_image("input.jpg", "output.jpg")
print(f"UUID: {metadata['uuid']}")

# Detect
result = processor.detect_text(protected_text)
if result['detected']:
    print(f"Found UUID: {result['uuid']}")
```

## Why "Blackwall"?

Blackwall is your defensive barrier - protecting both text and images from unauthorized AI training with:
- **Poisoning**: Degrades model performance
- **Watermarking**: Tracks where content is used
- **Unified System**: One tool for all content types
