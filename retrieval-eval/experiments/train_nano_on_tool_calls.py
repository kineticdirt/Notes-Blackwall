#!/usr/bin/env python3
"""
Train nano model (SmolLM3-3B) on MCP tool-call contents: unsupervised learning on
Tool → Arguments → Response text. Reads mcp_tool_calls.jsonl, formats as causal LM
corpus, runs one or more epochs (optional LoRA).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

CORPUS_JSONL = Path(__file__).parent / "mcp_tool_calls.jsonl"
SMOL_MODEL = "HuggingFaceTB/SmolLM3-3B-Base"
OUTPUT_DIR = Path(__file__).parent / "nano_trained_on_tools"


def format_tool_call_block(record: dict) -> str:
    """One training example: Tool + Arguments + Response (model learns to predict content)."""
    tool = record.get("tool", "")
    args = record.get("arguments", {})
    content = (record.get("content") or "").strip() or "(empty)"
    return f"Tool: {tool}\nArguments: {json.dumps(args)}\nResponse:\n{content}\n"


def build_corpus(path: Path) -> list[str]:
    blocks = []
    if not path.exists():
        return blocks
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                blocks.append(format_tool_call_block(record))
            except json.JSONDecodeError:
                continue
    return blocks


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Train nano on MCP tool-call contents (unsupervised).")
    parser.add_argument("--corpus", type=Path, default=CORPUS_JSONL, help="JSONL from mcp_collect_tool_calls.py")
    parser.add_argument("--out-dir", type=Path, default=OUTPUT_DIR, help="Output model/dataset dir")
    parser.add_argument("--epochs", type=float, default=1.0, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=1, help="Per-device batch size")
    parser.add_argument("--max-length", type=int, default=1024, help="Max token length per example")
    parser.add_argument("--lora", action="store_true", help="Use LoRA (peft) if available")
    parser.add_argument("--dry-run", action="store_true", help="Only build corpus and print stats, no training")
    args = parser.parse_args()

    blocks = build_corpus(args.corpus)
    if not blocks:
        print(f"No records in {args.corpus}. Run mcp_collect_tool_calls.py first.", file=sys.stderr)
        sys.exit(1)
    print(f"Corpus: {len(blocks)} blocks", flush=True)

    if args.dry_run:
        print("Dry run: corpus built. Run without --dry-run to train.")
        for i, b in enumerate(blocks[:2]):
            print(f"--- Block {i+1} (preview) ---\n{b[:500]}...")
        return

    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from datasets import Dataset

    tokenizer = AutoTokenizer.from_pretrained(SMOL_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def tokenize(examples):
        out = tokenizer(
            examples["text"],
            truncation=True,
            max_length=args.max_length,
            padding="max_length",
            return_tensors=None,
        )
        # Causal LM: labels = input_ids, -100 on padding (no loss on pad)
        labels = []
        for i, mask in enumerate(out["attention_mask"]):
            labels.append([id if mask[j] else -100 for j, id in enumerate(out["input_ids"][i])])
        out["labels"] = labels
        return out

    dataset = Dataset.from_dict({"text": blocks})
    dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
    dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    model = AutoModelForCausalLM.from_pretrained(SMOL_MODEL, device_map="auto", trust_remote_code=True)
    if args.lora:
        try:
            from peft import LoraConfig, get_peft_model, TaskType
            peft_config = LoraConfig(r=8, lora_alpha=16, task_type=TaskType.CAUSAL_LM, target_modules=["q_proj", "v_proj"])
            model = get_peft_model(model, peft_config)
            model.print_trainable_parameters()
        except ImportError:
            print("peft not installed; training full model.", file=sys.stderr)

    training_args = TrainingArguments(
        output_dir=str(args.out_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        save_strategy="no",
        logging_steps=1,
        report_to="none",
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )
    trainer.train()
    trainer.save_model(str(args.out_dir))
    tokenizer.save_pretrained(str(args.out_dir))
    print(f"Saved to {args.out_dir}", flush=True)


if __name__ == "__main__":
    main()
