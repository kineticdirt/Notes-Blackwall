#!/usr/bin/env python3
"""
Supervised fine-tune the nano (SmolLM3-3B) on Atlassian-only intent → JSON(tool, arguments).
Trains the model to emit **only valid JSON** (no hallucinated prose), improving routing accuracy.

Dataset: atlassian_intent_router_dataset.py → atlassian_intent_router.jsonl

Usage (from retrieval-eval/):
  python3 experiments/atlassian_intent_router_dataset.py
  python3 experiments/train_atlassian_intent_nano.py --epochs 3 --lora

Env: ATLASSIAN_NANO_MODEL_PATH=/path/to/output (optional; default experiments/atlassian_intent_nano_lora)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DEFAULT = ROOT / "atlassian_intent_router.jsonl"
SMOL_MODEL = "HuggingFaceTB/SmolLM3-3B-Base"
OUT_DEFAULT = ROOT / "atlassian_intent_nano_lora"


def load_rows(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="SFT nano on Atlassian intent→JSON routing.")
    ap.add_argument("--data", type=Path, default=DATA_DEFAULT)
    ap.add_argument("--out-dir", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--epochs", type=float, default=3.0)
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--max-length", type=int, default=512)
    ap.add_argument("--lora", action="store_true", default=True)
    ap.add_argument("--no-lora", action="store_true", help="Full fine-tune (heavy)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = load_rows(args.data)
    if not rows:
        print(f"No data in {args.data}. Run: python3 experiments/atlassian_intent_router_dataset.py", file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print(f"Dry run: {len(rows)} rows in {args.data}. Run without --dry-run to train (loads SmolLM3 + GPU).")
        return

    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from datasets import Dataset

    tokenizer = AutoTokenizer.from_pretrained(SMOL_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    input_ids_list = []
    labels_list = []
    for r in rows:
        inst = r.get("instruction", "")
        comp = r.get("completion", "")
        if not inst or not comp:
            continue
        i_ids = tokenizer(inst, add_special_tokens=True, truncation=False)["input_ids"]
        c_ids = tokenizer(comp, add_special_tokens=False, truncation=False)["input_ids"]
        c_ids = c_ids + [tokenizer.eos_token_id]
        full = i_ids + c_ids
        if len(full) > args.max_length:
            overflow = len(full) - args.max_length
            i_ids = i_ids[overflow:]
            full = i_ids + c_ids
            if len(full) > args.max_length:
                full = full[: args.max_length]
                c_len = len(c_ids)
                i_ids = full[:-c_len]
                c_ids = full[-c_len:]
        lab = [-100] * len(i_ids) + c_ids
        if len(lab) != len(full):
            full = i_ids + c_ids
            lab = [-100] * len(i_ids) + c_ids
        pad_len = args.max_length - len(full)
        if pad_len > 0:
            full = full + [tokenizer.pad_token_id] * pad_len
            lab = lab + [-100] * pad_len
        input_ids_list.append(full)
        labels_list.append(lab)

    print(f"Examples: {len(input_ids_list)}", flush=True)

    ds = Dataset.from_dict({"input_ids": input_ids_list, "labels": labels_list})
    attn = [[1 if tid != tokenizer.pad_token_id else 0 for tid in ids] for ids in input_ids_list]
    ds = ds.add_column("attention_mask", attn)

    model = AutoModelForCausalLM.from_pretrained(SMOL_MODEL, device_map="auto", trust_remote_code=True)
    use_lora = args.lora and not args.no_lora
    if use_lora:
        try:
            from peft import LoraConfig, get_peft_model, TaskType
            peft_config = LoraConfig(
                r=16,
                lora_alpha=32,
                task_type=TaskType.CAUSAL_LM,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                lora_dropout=0.05,
            )
            model = get_peft_model(model, peft_config)
            model.print_trainable_parameters()
        except ImportError:
            print("peft missing; pip install peft. Training full model.", file=sys.stderr)
            use_lora = False

    training_args = TrainingArguments(
        output_dir=str(args.out_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=2e-4,
        warmup_ratio=0.1,
        logging_steps=5,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=False,
    )

    class MaskPadCollator:
        def __call__(self, features):
            import torch
            input_ids = torch.tensor([f["input_ids"] for f in features], dtype=torch.long)
            attn = torch.tensor([f["attention_mask"] for f in features], dtype=torch.long)
            labels = torch.tensor([f["labels"] for f in features], dtype=torch.long)
            return {"input_ids": input_ids, "attention_mask": attn, "labels": labels}

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=MaskPadCollator(),
    )
    trainer.train()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(args.out_dir))
    tokenizer.save_pretrained(str(args.out_dir))
    meta = {"base_model": SMOL_MODEL, "task": "atlassian_intent_router_json", "train_rows": len(input_ids_list)}
    (args.out_dir / "atlassian_nano_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Saved to {args.out_dir}. Set ATLASSIAN_NANO_ADAPTER={args.out_dir} for inference.", flush=True)


if __name__ == "__main__":
    main()
