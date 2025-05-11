import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DATASET_NAME = os.getenv("DATASET_NAME", "bigcode/the-stack-github-issues")
DATASET_SPLIT = os.getenv("DATASET_SPLIT", "train")
SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 10000))
TARGET_REPO = os.getenv("TARGET_REPO", "numpy/numpy")
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
