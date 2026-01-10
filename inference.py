import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")


def load_model():
    try:
        print(f"Loading base model from {MODEL_NAME}")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=(
                torch.bfloat16
                if torch.cuda.is_available() and torch.cuda.is_bf16_supported()
                else torch.float32
            ),
            device_map="auto",
            trust_remote_code=True,
        )
        print("Base model loaded successfully")
        print(f"Loading tokenizer from {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        print("Tokenizer loaded successfully")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        if os.path.exists(OUTPUT_DIR) and any(
            (f.startswith("adapter_config") for f in os.listdir(OUTPUT_DIR))
        ):
            print(f"Loading LoRA adapter from {OUTPUT_DIR}")
            model = PeftModel.from_pretrained(model, OUTPUT_DIR, trust_remote_code=True)
            print("LoRA adapter loaded successfully")
        else:
            print("No LoRA adapter found, using base model only")
        return (model, tokenizer)
    except Exception as e:
        print(f"Error loading model: {e}")
        traceback.print_exc()
        return (None, None)


def generate_response(model, tokenizer, prompt):
    try:
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=8192,
                temperature=0.0,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        traceback.print_exc()
        return ""


def main():
    model, tokenizer = load_model()
    if model is None or tokenizer is None:
        print("Failed to load model or tokenizer")
        return
    alpaca_prompt = "<|im_start|>system\n{}<|im_end|>\n<|im_start|>user\n{}<|im_end|>\n<|im_start|>assistant\n"
    question = "Who are you?"
    system_prompt = (
        "You are an AI assistant for the Hyperlane Web framework written in Rust."
    )
    prompt = alpaca_prompt.format(system_prompt, question)
    print(f"Question: {question}")
    response = generate_response(model, tokenizer, prompt)
    print(f"Answer: {response}")


if __name__ == "__main__":
    main()
