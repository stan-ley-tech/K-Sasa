# ================================
# load_datasets.py
# Windows-safe K-Sasa dataset loader
# ================================

import os
from datasets import load_dataset

# -------------------------------
# 1. Suppress HF Hub symlink warnings
# -------------------------------
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# -------------------------------
# 2. Load FLORES-200 official dataset
# -------------------------------
print("Loading FLORES-200 dataset...")
try:
    flores_dataset = load_dataset("facebook/flores", "all")
    print("FLORES-200 loaded successfully!")
    print(f"Available splits: {list(flores_dataset.keys())}")
    print("Sample text from dev split:")
    print(flores_dataset["dev"][:1])
except Exception as e:
    print("Error loading FLORES-200:", e)

# -------------------------------
# 3. Load Swahili-English dataset (OPUS Books)
# -------------------------------
print("\nLoading Swahili-English dataset (OPUS Books)...")
try:
    swahili_dataset = load_dataset("opus_books", "sw-en")
    print("Swahili-English dataset loaded successfully!")
    print(f"Available splits: {list(swahili_dataset.keys())}")
    print("Sample text from train split:")
    print(swahili_dataset["train"][:1])
except Exception as e:
    print("Error loading Swahili-English dataset:", e)
    print("Listing available OPUS Books configs:")
    from datasets import load_dataset_builder
    builder = load_dataset_builder("opus_books")
    print(builder.builder_configs.keys())

# -------------------------------
# 4. Done
# -------------------------------
print("\nDataset loading complete. Ready for K-Sasa training!")
