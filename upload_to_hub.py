from huggingface_hub import HfApi, HfFolder
import os
import argparse
from dotenv import load_dotenv

load_dotenv()
HUGGING_FACE_REPO_ID = os.getenv("HUGGING_FACE_REPO_ID")
MODEL_DIR = os.getenv("OUTPUT_DIR")
REPO_ID = "hyperlane-dev/hyperlane-ai-training"
DATASET_DIR = "dataset"


def upload_model_to_hub():
    api = HfApi()
    token = HfFolder.get_token()
    if token is None:
        print(
            "Hugging Face token not found. Please log in using 'huggingface-cli login' or 'hf auth login'."
        )
        return
    try:
        user_info = api.whoami(token=token)
        username = user_info.get("name")
        print(f"Logged in as: {username}")
    except Exception as e:
        print(f"Error getting user info: {e}")
        print("Please ensure your token is valid.")
        return
    repo_owner = HUGGING_FACE_REPO_ID.split("/")[0]
    if username != repo_owner:
        print(
            f"Warning: You are logged in as '{username}', but the repository owner is '{repo_owner}'."
        )
        print(
            "Please make sure you have the necessary permissions to upload to this repository."
        )
    print(
        f"Preparing to upload the contents of '{MODEL_DIR}' to '{HUGGING_FACE_REPO_ID}'..."
    )
    try:
        api.create_repo(
            repo_id=HUGGING_FACE_REPO_ID, repo_type="model", exist_ok=True, token=token
        )
        print(f"Repository '{HUGGING_FACE_REPO_ID}' created or already exists.")
    except Exception as e:
        print(f"Error creating repository: {e}")
        return
    try:
        api.upload_folder(
            folder_path=MODEL_DIR,
            repo_id=HUGGING_FACE_REPO_ID,
            repo_type="model",
            token=token,
            commit_message=f"Upload fine-tuned model and GGUF file from training session.",
        )
        print(
            f"Successfully uploaded the contents of '{MODEL_DIR}' to '{HUGGING_FACE_REPO_ID}'."
        )
    except Exception as e:
        print(f"Error uploading folder: {e}")


def upload_dataset_to_hub():
    api = HfApi()
    token = HfFolder.get_token()
    if token is None:
        print(
            "Hugging Face token not found. Please log in using 'huggingface-cli login' or 'hf auth login'."
        )
        return
    try:
        user_info = api.whoami(token=token)
        username = user_info.get("name")
        print(f"Logged in as: {username}")
    except Exception as e:
        print(f"Error getting user info: {e}")
        print("Please ensure your token is valid.")
        return
    repo_owner = REPO_ID.split("/")[0]
    if username != repo_owner:
        print(
            f"Warning: You are logged in as '{username}', but the repository owner is '{repo_owner}'."
        )
        print(
            "Please make sure you have the necessary permissions to upload to this repository."
        )
    print(f"Preparing to upload the contents of '{DATASET_DIR}' to '{REPO_ID}'...")
    try:
        api.create_repo(
            repo_id=REPO_ID, repo_type="dataset", exist_ok=True, token=token
        )
        print(f"Dataset repository '{REPO_ID}' created or already exists.")
    except Exception as e:
        print(f"Error creating dataset repository: {e}")
        return
    try:
        api.upload_folder(
            folder_path=DATASET_DIR,
            repo_id=REPO_ID,
            repo_type="dataset",
            token=token,
            commit_message=f"Upload training dataset from {DATASET_DIR}.",
        )
        print(f"Successfully uploaded the contents of '{DATASET_DIR}' to '{REPO_ID}'.")
    except Exception as e:
        print(f"Error uploading dataset folder: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload model and/or dataset to Hugging Face Hub"
    )
    parser.add_argument(
        "target",
        nargs="?",
        choices=["model", "dataset"],
        help="Specify 'model' to upload only model, 'dataset' to upload only dataset. If not specified, both will be uploaded.",
    )
    args = parser.parse_args()
    if args.target == "model":
        upload_model_to_hub()
    elif args.target == "dataset":
        upload_dataset_to_hub()
    else:
        upload_model_to_hub()
        print("\n" + "=" * 50 + "\n")
        upload_dataset_to_hub()
