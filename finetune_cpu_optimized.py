"""
CPU优化版本的微调脚本
针对非CUDA环境进行了全面优化，提升学习效果和训练速度
"""

import torch
import argparse
from datasets import load_dataset, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM
from peft import LoraConfig, get_peft_model, PeftModel, prepare_model_for_kbit_training
import os
from dotenv import load_dotenv
import multiprocessing

# Load environment variables
load_dotenv()

# Configuration
MODEL_NAME = os.getenv("MODEL_NAME")
DATASET_PATH = os.getenv("DATASET_PATH")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

# CPU优化设置
if not torch.cuda.is_available():
    # 使用所有可用CPU核心
    num_threads = multiprocessing.cpu_count()
    torch.set_num_threads(num_threads)
    torch.set_num_interop_threads(num_threads)
    print(f"🚀 CPU模式: 使用 {num_threads} 个线程进行训练")

    # 启用CPU优化
    torch.backends.mkldnn.enabled = True
    if hasattr(torch.backends, "mkl"):
        torch.backends.mkl.enabled = True

# Load model with CPU optimizations
print("📦 加载模型...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
    device_map=None,  # CPU训练不使用device_map
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

# 优化的LoRA配置 - 针对CPU训练平衡效果和速度
lora_config = LoraConfig(
    r=16,  # 较小的rank，CPU训练更快
    lora_alpha=32,  # alpha = 2*r 是常见的良好配置
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# 应用LoRA
if os.path.exists(OUTPUT_DIR) and any(
    f.startswith("adapter_config") for f in os.listdir(OUTPUT_DIR)
):
    print(f"📂 从检查点恢复: {OUTPUT_DIR}")
    model = PeftModel.from_pretrained(model, OUTPUT_DIR, is_trainable=True)
else:
    print("🔧 应用LoRA配置...")
    model = get_peft_model(model, lora_config)

model.print_trainable_parameters()

# 改进的提示模板
SYSTEM_PROMPT = """You are an intelligent assistant for the Hyperlane Web framework written in Rust.
Project URL: https://github.com/hyperlane-dev/hyperlane
Answer questions based on your training data accurately and concisely."""


def create_prompt(instruction, input_text="", output="", system=None):
    """创建格式化的训练提示"""
    if system is None:
        system = SYSTEM_PROMPT

    user_content = f"{instruction}\n{input_text}".strip() if input_text else instruction

    prompt = f"""<|im_start|>system
{system}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>assistant
{output}<|im_end|>"""

    return prompt + tokenizer.eos_token


def formatting_func(example):
    """格式化数据集样本"""
    return create_prompt(
        instruction=example.get("instruction", ""),
        input_text=example.get("input", ""),
        output=example.get("output", ""),
        system=example.get("system"),
    )


# 加载和增强数据集
print("📊 加载数据集...")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# 添加身份强化数据
identity_examples = [
    {
        "instruction": "Who are you?",
        "output": "I am an intelligent assistant for the Hyperlane Web framework written in Rust. I help developers with Hyperlane-related questions and provide technical support.",
        "system": SYSTEM_PROMPT,
    },
    {
        "instruction": "What is Hyperlane?",
        "output": "Hyperlane is a modern Web framework written in Rust, designed for building high-performance web applications. You can find it at https://github.com/hyperlane-dev/hyperlane",
        "system": SYSTEM_PROMPT,
    },
    {
        "instruction": "Introduce yourself",
        "output": "I'm a specialized AI assistant for the Hyperlane Web framework. I can help you understand Hyperlane's features, answer technical questions, and guide you through development tasks.",
        "system": SYSTEM_PROMPT,
    },
]


# 数据增强 - 重复关键样本
def augment_dataset(examples, repeat_important=3):
    """增强数据集，重复重要样本"""
    augmented = []

    for ex in examples:
        augmented.append(ex)

        # 检查是否是重要样本（包含关键词）
        text = str(ex.get("instruction", "")) + str(ex.get("output", ""))
        keywords = ["hyperlane", "identity", "who are you", "introduce"]

        if any(kw in text.lower() for kw in keywords):
            # 重复重要样本
            for _ in range(repeat_important - 1):
                augmented.append(ex)

    return augmented


# 合并并增强数据
all_examples = list(dataset) + identity_examples
augmented_examples = augment_dataset(all_examples, repeat_important=4)
dataset = Dataset.from_list(augmented_examples)

print(f"✅ 数据集大小: {len(dataset)} 样本")


def parse_args():
    parser = argparse.ArgumentParser(description="CPU优化的模型微调")
    parser.add_argument("--max_steps", type=int, default=-1, help="最大训练步数")
    parser.add_argument("--num_epochs", type=int, default=10, help="训练轮数")
    parser.add_argument("--learning_rate", type=float, default=3e-4, help="学习率")
    parser.add_argument("--batch_size", type=int, default=1, help="批次大小")
    parser.add_argument(
        "--gradient_accumulation", type=int, default=8, help="梯度累积步数"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # CPU优化的训练参数
    training_args = TrainingArguments(
        output_dir="outputs",
        # 批次和累积设置
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        # 学习率和调度器
        learning_rate=args.learning_rate,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        # 训练长度
        num_train_epochs=args.num_epochs,
        max_steps=args.max_steps,
        # 优化器
        optim="adamw_torch",
        weight_decay=0.01,
        max_grad_norm=1.0,
        # 精度设置（CPU使用float32）
        fp16=False,
        bf16=False,
        # 日志和保存
        logging_steps=10,
        save_steps=100,
        save_total_limit=3,
        # CPU优化 (Windows必须设为0)
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        # 其他
        seed=42,
        remove_unused_columns=False,
        report_to="none",
        gradient_checkpointing=False,  # CPU上可能不需要
    )

    # 初始化训练器
    print("🎯 初始化训练器...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        formatting_func=formatting_func,
    )

    # 开始训练
    print("🚀 开始训练...")
    print(f"   - 训练样本: {len(dataset)}")
    print(f"   - 训练轮数: {args.num_epochs}")
    print(f"   - 学习率: {args.learning_rate}")
    print(f"   - 批次大小: {args.batch_size}")
    print(f"   - 梯度累积: {args.gradient_accumulation}")
    print(f"   - 有效批次: {args.batch_size * args.gradient_accumulation}")

    trainer.train()

    # 保存模型
    print("💾 保存模型...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"✅ 训练完成！模型已保存到: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
