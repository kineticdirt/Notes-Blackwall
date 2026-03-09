# Blackwall: Autonomous AI Protection System

Blackwall is a **collection of autonomous AI tools** that operate independently to protect and track content. It extends the Nightshade tracker concept to protect both **text and image** content from unauthorized AI training, with agents that work autonomously to achieve goals.

## Overview

Blackwall extends the Nightshade concept to:
- **Text Data**: Adversarial text poisoning + watermarking
- **Image Data**: Adversarial image poisoning + watermarking (from Nightshade)
- **Multi-Modal Protection**: Unified system for both content types

## Key Features

### Text Protection
- **Text Poisoning**: Adversarial perturbations in text embeddings
- **Text Watermarking**: Steganographic UUID embedding in text
- **Robust Tracking**: Survives paraphrasing, summarization, translation

### Image Protection
- **Image Poisoning**: Adversarial perturbations (Nightshade-style)
- **Image Watermarking**: DCT-based steganography
- **Multi-format Support**: JPG, PNG, WebP

### Unified System
- **Single Registry**: Track both text and images
- **Cross-Modal Detection**: Find content across formats
- **Complete Audit Trail**: Full usage tracking

## Architecture

```
blackwall/
├── autonomous/                 # Autonomous AI system
│   ├── orchestrator.py       # Autonomous goal orchestrator
│   ├── autonomous_agent.py   # Base autonomous agent
│   ├── self_coordinator.py   # Self-coordinating agents
│   └── autonomous_protection_agent.py  # Autonomous protection
├── core/
│   ├── text_poisoning.py      # Text adversarial poisoning
│   ├── text_watermarking.py   # Text steganography
│   ├── unified_processor.py   # Unified text + image processor
├── database/
│   └── registry.py            # Extended registry for text + images
├── cli.py                     # Standard CLI
└── autonomous_cli.py          # Autonomous CLI
```

## Autonomous Operation

**Blackwall operates autonomously** - agents make decisions, coordinate, and achieve goals independently:

- **Autonomous Goal Achievement**: Set goals, agents work independently
- **Self-Coordination**: Agents discover and work together automatically
- **Autonomous Decision Making**: Agents make context-aware decisions
- **Self-Healing**: Automatic error recovery and adaptation

## Use Cases

### Text Protection
- Protect written content (articles, stories, code)
- Track where text is used in training datasets
- Poison text to degrade model performance

### Image Protection
- Protect artwork and images
- Track image usage in datasets
- Poison images to degrade vision models

### Multi-Modal Protection
- Protect complete works (text + images)
- Track usage across modalities
- Comprehensive legal evidence

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Autonomous Mode (Recommended)

**Set autonomous goals** - agents work independently:

```bash
# Set a goal - agents work autonomously
python autonomous_cli.py achieve "Protect all content in project"

# Autonomous protection
python autonomous_cli.py protect document.txt
python autonomous_cli.py batch-protect ./content/

# Check autonomous status
python autonomous_cli.py status

# Coordinate agents for complex tasks
python autonomous_cli.py coordinate "Protect, test, and document"
```

### Standard Mode

**Direct commands** for specific operations:

```bash
# Protect text
python cli.py process-text -i document.txt -o document_protected.txt

# Protect image
python cli.py process-image -i image.jpg -o image_protected.jpg

# Detect content
python cli.py detect -i suspicious_content.txt
python cli.py detect -i suspicious_image.jpg
```

See [README_AUTONOMOUS.md](README_AUTONOMOUS.md) for full autonomous system documentation.

## Why "Blackwall"?

Blackwall represents a defensive barrier against unauthorized AI training - protecting your content (text and images) with both poisoning and tracking capabilities.
