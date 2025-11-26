import os
from datasets import load_dataset

# 1. Folder to save datasets
os.makedirs("data", exist_ok=True)

# 2. Load Tatoeba Swahili-English
print("Loading Tatoeba Swahili-English dataset...")
swahili_dataset = load_dataset("tatoeba", "sw-eng")
print(swahili_dataset)

# 3. Save train split to parquet
out_path = os.path.join("data", "tatoeba_sw_eng_train.parquet")
swahili_dataset["train"].to_parquet(out_path)
print(f"Dataset saved at {out_path}")
