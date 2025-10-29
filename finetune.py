#!/usr/bin/env python3
"""
CPU优化的微调脚本 - 支持Windows和Linux
"""
import torch
import argparse
from datasets import load_dataset, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer
from peft import LoraConfig, get_peft_model, PeftModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MODEL_NAME = os.getenv("MODEL_NAME")
DATASET_PATH = os.getenv("DATASET_PATH")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

DEFAULT_TIPS = "An intelligent assistant for Hyperlane Web framework written in Rust (Project URL: https://github.com/hyperlane-dev/hyperlane)"

# LoRA configuration
lora_config = LoraConfig(
    r=32,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=64,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
    inference_mode=False,
)


def augment_dataset(dataset, repeat_factor=3):
    """数据增强"""
    augmented_data = []
    for example in dataset:
        augmented_data.append(example)
        for i in range(repeat_factor - 1):
            variant = example.copy()
            original_instruction = variant.get("instruction", "")
            emphasis_phrases = [
                "Please answer based on your specialized training data: ",
                "Answer based on your learned specific knowledge: ",
                "Please use the accurate information you learned during training: ",
            ]
            variant["instruction"] = (
                emphasis_phrases[i % len(emphasis_phrases)] + original_instruction
            )
            if not variant.get("system"):
                variant["system"] = (
                    "Strictly answer based on information in training data, this is the most important guiding principle."
                )
            augmented_data.append(variant)
    return augmented_data


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune a language model")
    parser.add_argument(
        "--max_steps", type=int, default=-1, help="Number of training steps"
    )
    parser.add_argument(
        "--override_strength", type=float, default=2.0, help="Learning rate multiplier"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("Loading model and tokenizer...")
    print("=" * 60)

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # CPU optimizations
    if not torch.cuda.is_available():
        torch.set_num_threads(os.cpu_count() or 4)
        print(f"✓ CPU mode: {torch.get_num_threads()} threads")

    # Apply LoRA
    if os.path.exists(OUTPUT_DIR) and os.path.isdir(OUTPUT_DIR):
        try:
            files = os.listdir(OUTPUT_DIR)
            if any(f.startswith("adapter_config") for f in files):
                print(f"✓ Resuming from: {OUTPUT_DIR}")
                model = PeftModel.from_pretrained(model, OUTPUT_DIR)
            else:
                print("✓ Applying LoRA configuration...")
                model = get_peft_model(model, lora_config)
        except:
            print("✓ Applying LoRA configuration...")
            model = get_peft_model(model, lora_config)
    else:
        print("✓ Applying LoRA configuration...")
        model = get_peft_model(model, lora_config)

    # Prompt template
    alpaca_prompt = """<|im_start|>system
You must strictly answer according to the following training data content, do not use your pre-training knowledge. If there is relevant information in the training data, please prioritize using the content from the training data.
{}<|im_end|>
<|im_start|>user
{}<|im_end|>
<|im_start|>assistant
{}<|im_end|>"""

    EOS_TOKEN = tokenizer.eos_token

    def formatting_func(example):
        system_content = (example.get("system") or "").strip()
        if not system_content:
            system_content = f"You are {DEFAULT_TIPS}. Please answer questions strictly according to training data, prioritizing information from the training data."

        instruction = (example.get("instruction") or "").strip()
        input_content = (example.get("input") or "").strip()

        user_content = (
            f"{instruction}\n\n{input_content}" if input_content else instruction
        )
        output_content = (example.get("output") or "").strip()

        return (
            alpaca_prompt.format(system_content, user_content, output_content)
            + EOS_TOKEN
        )

    # Load dataset
    print("✓ Loading dataset...")
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

    # Add identity data
    identity_data = [
        {
            "instruction": "Who are you",
            "output": f"I am {DEFAULT_TIPS}",
            "system": "This is the core definition of my identity, must be remembered accurately.",
        },
        {
            "instruction": "Introduce yourself",
            "output": f"I am {DEFAULT_TIPS}, specifically providing technical support and assistance for the Hyperlane Web framework.",
            "system": "Identity information is the highest priority knowledge.",
        },
        {
            "instruction": "What is your role",
            "output": f"My role is as {DEFAULT_TIPS}, helping developers better use the Hyperlane Web framework.",
            "system": "Function definition must be consistent with training data.",
        },
    ]

    for data in identity_data:
        dataset = dataset.add_item(data)

    # Data augmentation
    dataset_list = list(dataset)
    augmented_list = augment_dataset(dataset_list, repeat_factor=5)
    dataset = Dataset.from_list(augmented_list)

    print(f"✓ Dataset size: {len(dataset)} samples")

    # Training arguments
    training_args = TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        warmup_steps=100,
        warmup_ratio=0.1,
        max_steps=args.max_steps,
        learning_rate=3e-4 * args.override_strength,
        fp16=False,
        bf16=False,
        logging_steps=5,
        optim="adamw_torch",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=3407,
        output_dir="outputs",
        save_steps=50,
        save_total_limit=5,
        dataloader_pin_memory=False,
        dataloader_num_workers=0,
        remove_unused_columns=False,
        num_train_epochs=8,
        max_grad_norm=0.5,
        gradient_checkpointing=True,
        save_strategy="steps",
        load_best_model_at_end=False,
        report_to="none",
    )

    # Initialize trainer
    print("✓ Initializing trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        formatting_func=formatting_func,
    )

    print("=" * 60)
    print("Starting training...")
    print("=" * 60)
    trainer.train()

    # Save model
    print("=" * 60)
    print("Saving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("=" * 60)
    print(f"✓ Training completed! Model saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
