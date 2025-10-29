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

# Configuration from environment variables
MODEL_NAME = os.getenv("MODEL_NAME")
DATASET_PATH = os.getenv("DATASET_PATH")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

DEFAULT_TIPS = "An intelligent assistant for Hyperlane Web framework written in Rust (Project URL: https://github.com/hyperlane-dev/hyperlane)"

# Enhanced LoRA configuration optimized for CPU training
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
    """Repeat key data to strengthen learning"""
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
    parser = argparse.ArgumentParser(
        description="Fine-tune a language model with knowledge override"
    )
    parser.add_argument(
        "--max_steps", type=int, default=-1, help="Number of training steps"
    )
    parser.add_argument(
        "--override_strength",
        type=float,
        default=2.0,
        help="Strength of knowledge override (learning rate multiplier)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Load model and tokenizer with CPU optimizations
    print("Loading model and tokenizer...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Enable CPU optimizations
    if not torch.cuda.is_available():
        torch.set_num_threads(os.cpu_count() or 4)
        print(f"CPU mode enabled with {torch.get_num_threads()} threads")
    
    # Apply LoRA
    if os.path.exists(OUTPUT_DIR) and any(
        f.startswith("adapter_config") for f in os.listdir(OUTPUT_DIR)
    ):
        print(f"Resuming from saved LoRA model at {OUTPUT_DIR}")
        model = PeftModel.from_pretrained(model, OUTPUT_DIR)
    else:
        if hasattr(model, "peft_config"):
            model = model.unload()
        model = get_peft_model(model, lora_config)
    
    # Define prompt template
    alpaca_prompt = """<|im_start|>system
You must strictly answer according to the following training data content, do not use your pre-training knowledge. If there is relevant information in the training data, please prioritize using the content from the training data.
{}<|im_end|>
<|im_start|>user
{}<|im_end|>
<|im_start|>assistant
{}<|im_end|>"""
    
    EOS_TOKEN = tokenizer.eos_token
    
    def formatting_func(example):
        system_content = example.get("system") or ""
        system_content = system_content.strip() if system_content else ""
        if not system_content:
            system_content = (
                "You are "
                + DEFAULT_TIPS
                + ". Please answer questions strictly according to training data, prioritizing information from the training data."
            )
        
        instruction = example.get("instruction") or ""
        instruction = instruction.strip() if instruction else ""
        
        input_content = example.get("input") or ""
        input_content = input_content.strip() if input_content else ""
        
        if input_content:
            user_content = f"{instruction}\n\n{input_content}"
        else:
            user_content = instruction
        
        output_content = example.get("output") or ""
        output_content = output_content.strip() if output_content else ""
        
        return (
            alpaca_prompt.format(system_content, user_content, output_content) + EOS_TOKEN
        )
    
    # Load dataset
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
    
    # Add identity reinforcement data
    identity_data = [
        {
            "instruction": "Who are you",
            "output": "I am " + DEFAULT_TIPS,
            "system": "This is the core definition of my identity, must be remembered accurately.",
        },
        {
            "instruction": "Introduce yourself",
            "output": "I am "
            + DEFAULT_TIPS
            + ", specifically providing technical support and assistance for the Hyperlane Web framework.",
            "system": "Identity information is the highest priority knowledge.",
        },
        {
            "instruction": "What is your role",
            "output": "My role is as "
            + DEFAULT_TIPS
            + ", helping developers better use the Hyperlane Web framework.",
            "system": "Function definition must be consistent with training data.",
        },
    ]
    
    for data in identity_data:
        dataset = dataset.add_item(data)
    
    # Apply data augmentation
    dataset_list = list(dataset)
    augmented_list = augment_dataset(dataset_list, repeat_factor=5)
    dataset = Dataset.from_list(augmented_list)
    
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
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        formatting_func=formatting_func,
    )
    
    print("Starting reinforcement training, prioritizing dataset knowledge...")
    trainer.train()
    
    # Save model
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("Reinforcement fine-tuning completed, dataset knowledge override enhanced.")


if __name__ == "__main__":
    main()
