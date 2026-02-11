---
name: protection
description: Protect content using text and image poisoning and watermarking
version: 1.0.0
tools: [read_file, write_file, glob_file_search]
resources: [content-files, registry]
metadata:
  category: security
  complexity: high
---

# Protection Skill

Protect content from unauthorized AI training using adversarial poisoning and watermarking techniques.

## Workflow

1. Identify content to protect (text or images)
2. Generate unique UUID for tracking
3. Apply adversarial poisoning
4. Embed watermark/steganographic marker
5. Register in tracking database
6. Verify protection was applied correctly

## Examples

- Protect a single document
- Batch protect all images in a directory
- Protect code repositories
- Track content usage across platforms
- Generate protection reports
