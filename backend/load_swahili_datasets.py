import os
from datasets import load_dataset

# 1. Set local save path
save_path = os.path.join(os.getcwd(), "data")
os.makedirs(save_path, exist_ok=True)

# 2. Load FLORES-200 Swahili dataset
print("Loading FLORES-200 Swahili dataset...")
flores = load_dataset("facebook/flores200", "sw")
flores_train_path = os.path.join(save_path, "flores_sw_train.parquet")
flores["train"].to_parquet(flores_train_path)
print(f"FLORES-200 saved at {flores_train_path}")

# 3. Load Tatoeba Swahili-English dataset
print("Loading Tatoeba Swahili-English dataset...")
tatoeba = load_dataset("tatoeba", "sw-eng")
tatoeba_train_path = os.path.join(save_path, "tatoeba_sw_eng_train.parquet")
tatoeba["train"].to_parquet(tatoeba_train_path)
print(f"Tatoeba dataset saved at {tatoeba_train_path}")

print("All datasets downloaded and saved successfully.")
