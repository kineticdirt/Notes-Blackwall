# Nightshade Tracker — Image Protection

**Nightshade-tracker** provides image protection: poisoning and watermarking. Blackwall’s [[Core-Protection]] uses it when the package is on path; it can also be used standalone. See [[Core-Protection]] for the unified processor and [[Blackwall-Agents]] for agents that use it.

---

## Location

- **Path**: `nightshade-tracker/`
- **Key modules**: `core/` (poisoning, watermarking, image_processor, detector), `database/registry.py`, `utils/` (ecc, perceptual_hash), `cli.py`

---

## Components

- **core/poisoning.py**: Adversarial poisoning for images (e.g. training-time robustness).
- **core/watermarking.py**: Robust watermarking for images.
- **core/image_processor.py**: Image loading and preprocessing.
- **core/detector.py**: Detection of watermarks/poison in images.
- **core/text_poisoning.py**, **core/text_watermarking.py**, **core/text_processor.py**: Text-side support within nightshade-tracker.
- **database/registry.py**: Registry for tracked/protected content.
- **utils/ecc.py**, **utils/perceptual_hash.py**: Utilities for robustness and hashing.
- **cli.py**: CLI for protect/detect and related commands.

---

## Integration with Blackwall

- **UnifiedProcessor** (`blackwall/core/unified_processor.py`) imports from `nightshade-tracker` when the path exists: `AdversarialPoisoner`, `RobustWatermarker`, `ImageProcessor`.
- If nightshade-tracker is not available, Blackwall’s image processing is disabled; text processing still works.

---

## Docs in Repo

- **README.md**, **QUICKSTART.md**: Usage and setup.
- **TRACKING.md**, **SUBTLE_POISONING.md**, **TEXT_POISONING.md**: Design and behavior.

---

## Related

- [[Core-Protection]] — UnifiedProcessor and text modules.
- [[Blackwall-Agents]] — Protection and detection agents.
- [[index]] — Compendium index.
