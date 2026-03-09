# Nightshade Tracker: Poisoning-Concurrent Watermarking System

A cutting-edge system that combines adversarial poisoning with robust watermarking/tracking for **images** (JPG, PNG, WebP) and **text files**.

## Overview

This system implements **"Poisoning-Concurrent Watermarking"** - a dual-objective approach that:

### For Images:
1. **Poisons images** to degrade AI model training (adversarial perturbations)
2. **Embeds robust tracking signals** (UUID + perceptual hash) that survive compression, resizing, and screenshots
3. **Maintains a registry** to track where images are being used and build complete usage trails

### For Text:
1. **Poisons text** by inserting disruptive words that ruin content quality and are semi-useless
2. **Embeds invisible watermarks** (UUID via zero-width unicode) that survive copy/paste and paraphrasing
3. **Tracks text usage** in datasets and builds complete usage trails

## Key Features

### Image Protection
- **Multi-Format Support**: JPG, PNG, WebP
- **Dual-Layer Tracking**: 
  - Invisible steganographic seal (128-256 bit UUID)
  - Perceptual hash (pHash) fingerprint
- **Redundancy & Error Correction**: Reed-Solomon codes for 95%+ reliability
- **Multi-Objective Optimization**: Balances poisoning utility with watermark robustness

### Text Protection
- **Text Format Support**: TXT, MD, PY, JS, HTML, JSON, XML, CSV
- **Disruptive Word Insertion**: Inserts semi-useless words that ruin content quality
- **Invisible Watermarking**: UUID embedded via zero-width unicode characters
- **Robust Tracking**: Survives copy/paste, paraphrasing, and translation

### Unified System
- **Database Registry**: SQLite-based tracking for both images and text
- **Complete Usage Trails**: Track where content is used across datasets and websites

## Architecture

```
nightshade-tracker/
├── core/
│   ├── image_processor.py      # Image format handling (JPG, PNG, WebP)
│   ├── text_processor.py       # Text format handling (TXT, MD, etc.)
│   ├── watermarking.py         # Image steganography with ECC
│   ├── text_watermarking.py    # Text steganography (zero-width unicode)
│   ├── poisoning.py            # Image adversarial perturbations
│   ├── text_poisoning.py        # Text disruptive word insertion
│   ├── optimizer.py            # Multi-objective optimization (images)
│   └── detector.py             # Watermark extraction & matching
├── database/
│   └── registry.py             # SQLite database for tracking (images + text)
├── utils/
│   ├── perceptual_hash.py      # pHash generation
│   └── ecc.py                  # Error correction codes
└── cli.py                      # Command-line interface
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Process Images (Add Poison + Watermark)

```bash
python cli.py process --input image.jpg --output image_processed.jpg --poison-strength 0.1
```

### Process Text Files (Add Poison + Watermark)

```bash
python cli.py process-text --input document.txt --output document_processed.txt --poison-strength 0.1
```

### Detect Watermarks

```bash
# Detect in image
python cli.py detect --input suspicious_image.jpg

# Detect in text
python cli.py detect-text --input suspicious_document.txt
```

### Scan Dataset for Matches

```bash
python cli.py scan --dataset /path/to/dataset --output matches.json
```

### List Registered Content

```bash
# List images
python cli.py list

# List text files
python cli.py list-text
```

## Technical Details

### Multi-Objective Loss Function

```
Total_Loss = Poison_Loss + (Alpha * Watermark_Loss)
```

Where:
- `Poison_Loss`: Adversarial perturbation strength
- `Watermark_Loss`: Steganographic embedding quality
- `Alpha`: Balance parameter (default: 0.5)

### Redundancy Strategy

- UUID embedded 10-20 times across different image regions
- Reed-Solomon error correction (can recover from 30% data loss)
- Frequency-domain separation (poison in some frequencies, watermark in others)

## Tracking & Usage Trails

This system builds **complete usage trails** to track where your images are being used:

1. **Process image** → UUID + pHash stored in registry
2. **Scan datasets/websites** → System detects watermarked images
3. **Log detections** → Every detection is logged with source, dataset, URL, timestamp
4. **Build trail** → See complete history of where each image has been found

### Key Tracking Features

- **Source Tracking**: Logs where images are found (datasets, websites, APIs)
- **Dataset Identification**: Tracks which datasets contain your images
- **Usage Statistics**: Aggregates detection data for reporting
- **Complete Audit Trail**: Every detection includes full context (URLs, metadata, timestamps)

See [TRACKING.md](TRACKING.md) for detailed tracking documentation.

## Research References

- NeurIPS 2025: Poisoning-Concurrent Watermarking
- Nightshade: Adversarial Image Poisoning
- InvisMark: Robust Steganography (2024)
