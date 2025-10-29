import torch
import argparse
from datasets import load_dataset
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

# Load model and tokenizer with CPU optimizations
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float32,  # CPU works best with float32
    low_cpu_mem_usage=True,  # Optimize CPU memory usage
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)

# Enable CPU optimizations
if not torch.cuda.is_available():
    torch.set_num_threads(os.cpu_count() or 4)  # Use all CPU cores
    print(f"CPU mode enabled with {torch.get_num_threads()} threads")

# Set pad token if it doesn't exist
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Enhanced LoRA configuration optimized for CPU training
lora_config = LoraConfig(
    r=32,  # Reduced rank for CPU efficiency while maintaining effectiveness
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=64,  # Balanced alpha for stable CPU training
    lora_dropout=0.1,  # Higher dropout to prevent overfitting on CPU
    bias="none",  # Reduce parameters for CPU efficiency
    task_type="CAUSAL_LM",
    inference_mode=False,
)

# Check if there's a saved LoRA model to resume from
if os.path.exists(OUTPUT_DIR) and any(
    f.startswith("adapter_config") for f in os.listdir(OUTPUT_DIR)
):
    print(f"Resuming from saved LoRA model at {OUTPUT_DIR}")
    model = PeftModel.from_pretrained(model, OUTPUT_DIR)
else:
    if hasattr(model, "peft_config"):
        model = model.unload()
    model = get_peft_model(model, lora_config)

# Enhanced prompt formatting with stronger emphasis on dataset knowledge
alpaca_prompt = """<|im_start|>system
You must strictly answer according to the following training data content, do not use your pre-training knowledge. If there is relevant information in the training data, please prioritize using the content from the training data.
{}<|im_end|>
<|im_start|>user
{}<|im_end|>
<|im_start|>assistant
{}<|im_end|>"""

EOS_TOKEN = tokenizer.eos_token

DEFAULT_TIPS = "An intelligent assistant for Hyperlane Web framework written in Rust (Project URL: https://github.com/hyperlane-dev/hyperlane)"


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


# Data augmentation function to reinforce dataset knowledge
def augment_dataset(dataset, repeat_factor=3):
    """Repeat key data to strengthen learning"""
    augmented_data = []

    for example in dataset:
        # Original data
        augmented_data.append(example)

        # Generate variants to reinforce memory
        for i in range(repeat_factor - 1):
            variant = example.copy()

            # Add emphasis phrases to instruction
            original_instruction = variant.get("instruction", "")
            emphasis_phrases = [
                "Please answer based on your specialized training data: ",
                "Answer based on your learned specific knowledge: ",
                "Please use the accurate information you learned during training: ",
            ]
            variant["instruction"] = (
                emphasis_phrases[i % len(emphasis_phrases)] + original_instruction
            )

            # Emphasize using training data in system prompt
            if not variant.get("system"):
                variant["system"] = (
                    "Strictly answer based on information in training data, this is the most important guiding principle."
                )

            augmented_data.append(variant)

    return augmented_data


# Load and format dataset
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

# Add identity data to dataset
for data in identity_data:
    dataset = dataset.add_item(data)

# Apply data augmentation
dataset_list = list(dataset)
augmented_list = augment_dataset(
    dataset_list, repeat_factor=5
)  # Repeat 5 times to strengthen

# Convert back to dataset format
from datasets import Dataset

dataset = Dataset.from_list(augmented_list)


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


# Parse command line arguments
args = parse_args()

# Optimized training arguments for CPU with better learning
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,  # Larger accumulation for stable gradients
    warmup_steps=100,  # More warmup for stable CPU training
    warmup_ratio=0.1,  # 10% of training for warmup
    max_steps=args.max_steps,
    learning_rate=3e-4 * args.override_strength,  # Higher LR for better learning
    fp16=False,  # Disable fp16 on CPU
    bf16=False,  # Disable bf16 on CPU
    logging_steps=5,
    optim="adamw_torch",  # Standard optimizer for CPU
    weight_decay=0.01,
    lr_scheduler_type="cosine",  # Cosine annealing for smooth learning
    seed=3407,
    output_dir="outputs",
    save_steps=50,  # Save more frequently
    save_total_limit=5,  # Keep fewer checkpoints to save disk
    dataloader_pin_memory=False,  # Disable for CPU
    dataloader_num_workers=2,  # Use workers for data loading
    remove_unused_columns=False,
    num_train_epochs=8,  # More epochs for CPU training
    max_grad_norm=0.5,  # Gradient clipping for stability
    gradient_checkpointing=True,  # Save memory
    save_strategy="steps",
    load_best_model_at_end=False,
    report_to="none",  # Disable reporting for speed
)


# Custom data collator for emphasis on specific examples
class KnowledgeOverrideDataCollator:
    def __init__(self, tokenizer, emphasis_keywords=None):
        self.tokenizer = tokenizer
        self.emphasis_keywords = emphasis_keywords or [
            "identity",
            "who are you",
            "role",
            "Hyperlane",
        ]

    def __call__(self, examples):
        # Give higher weight to samples containing keywords
        batch = []
        for example in examples:
            # Check if contains emphasis keywords
            text = str(example.get("input_ids", ""))
            is_important = any(keyword in text for keyword in self.emphasis_keywords)

            if is_important:
                # Repeat important samples to enhance learning
                batch.extend([example] * 3)
            else:
                batch.append(example)

        return batch


# Initialize trainer with CPU-optimized settings
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    formatting_func=formatting_func,
    max_seq_length=512,  # Limit sequence length for CPU efficiency
    packing=False,  # Disable packing for better learning quality
    dataset_text_field=None,  # Use formatting_func
)


# Custom training loop with knowledge reinforcement
class KnowledgeReinforcementCallback:
    def on_epoch_begin(self, logs=None):
        print(
            "Starting new training epoch, focusing on strengthening dataset knowledge..."
        )

    def on_step_end(self, step, logs=None):
        if step % 100 == 0:
            print(
                f"Step {step}: Continuously strengthening dataset knowledge override..."
            )


# Add callback
# trainer.add_callback(KnowledgeReinforcementCallback())

print("Starting reinforcement training, prioritizing dataset knowledge...")
trainer.train()

# Save the model
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Reinforcement fine-tuning completed, dataset knowledge override enhanced.")
