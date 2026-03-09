# Core Protection — Text/Image Poisoning, Watermarking, Unified Processor

**Core protection** in Blackwall handles text and image poisoning and watermarking via a unified processor and registry. Used by [[Blackwall-Agents]] and [[Autonomous-System]]. Image logic is delegated to [[Nightshade-Tracker]] when available.

---

## Location

- **Path**: `blackwall/core/`
- **Key files**: `unified_processor.py`, `text_poisoning.py`, `text_watermarking.py`
- **Registry**: `blackwall/database/registry.py`

---

## Unified Processor (`unified_processor.py`)

`UnifiedProcessor` — single entry for text and image protection and detection.

- **Text**: Uses `TextPoisoner` and `TextWatermarker` from `core/`.
- **Image**: If `nightshade-tracker` is on path, uses `AdversarialPoisoner`, `RobustWatermarker`, `ImageProcessor`; otherwise image ops are unavailable.
- **Init**: `poison_strength`, `watermark_strength`; initializes text and (optional) image processors.
- **Text**: `process_text(text)` → (processed_text, metadata); `detect_text(text)` → result dict (detected, uuid, etc.).
- **Image**: `process_image(path)` → (output_path, metadata); `detect_image(path)` → result dict.
- **Metadata**: Typically includes uuid, poison_strength, watermark_method, content_type.

---

## Text Poisoning (`text_poisoning.py`)

- **TextPoisoner**: Applies subtle perturbations to text (e.g. for training-time or inference-time robustness); strength configurable.
- Used by UnifiedProcessor as step after watermarking for text.

---

## Text Watermarking (`text_watermarking.py`)

- **TextWatermarker**: Embeds and extracts watermarks (e.g. unicode-based); `embed(text, method="unicode")`, `get_uuid()`.
- Used by UnifiedProcessor for text; UUID is stored in registry.

---

## Registry (`blackwall/database/registry.py`)

- **BlackwallRegistry**: Registers and looks up protected content by UUID (original_path, uuid, content_type, etc.).
- **Methods**: `register_content(...)`, `lookup_by_uuid(uuid)`.
- Used by Detection and Protection agents and AutonomousProtectionAgent.

---

## Data Flow

1. **Protection**: User/content path → UnifiedProcessor.process_text / process_image → watermarked + poisoned output; metadata (uuid) → registry.
2. **Detection**: Content path or text → UnifiedProcessor.detect_text / detect_image → result (detected, uuid); optional registry lookup by uuid.

---

## Related

- [[Blackwall-Agents]] — DetectionAgent, ProtectionAgent use UnifiedProcessor and registry.
- [[Autonomous-System]] — AutonomousProtectionAgent uses UnifiedProcessor and registry.
- [[Nightshade-Tracker]] — Image poisoning/watermarking implementation when available.
- [[index]] — Compendium index.
