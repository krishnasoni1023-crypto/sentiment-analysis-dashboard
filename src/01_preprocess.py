# -*- coding: utf-8 -*-
"""
01_preprocess.py
----------------
Step 1 & 2 of the pipeline:
  - Load the Kaggle Amazon Reviews Polarity CSV
  - Sample rows (configurable)
  - Clean text (HTML, URLs, special chars, lowercase)
  - Export a clean parquet file for the next step

Usage:
    python src/01_preprocess.py

Input:
    data/amazon_review_polarity_csv/train.csv

Output:
    data/reviews_clean.parquet

Dataset schema (no header row):
    col 0 -> polarity   : 1 = Negative (1-2 stars), 2 = Positive (4-5 stars)
    col 1 -> title      : review title (used as product_name)
    col 2 -> text       : full review body
"""

import io
import re
import sys
import pathlib
import pandas as pd
from tqdm import tqdm

# Force UTF-8 output so tqdm / print work on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# -- Paths -------------------------------------------------------------------
ROOT        = pathlib.Path(__file__).resolve().parents[1]
RAW_CSV     = ROOT / "data" / "amazon_review_polarity_csv" / "train.csv"
CLEAN_OUT   = ROOT / "data" / "reviews_clean.parquet"

# -- Config ------------------------------------------------------------------
SAMPLE_SIZE = 2_000   # Set to None to use full dataset
RANDOM_SEED = 42


# -- Helpers -----------------------------------------------------------------
def clean_text(text: str) -> str:
    """Remove HTML tags, URLs, special characters; lowercase."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"<[^>]+>", " ", text)            # strip HTML tags
    text = re.sub(r"http\S+|www\.\S+", " ", text)   # remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)     # keep alphanumeric + spaces
    text = re.sub(r"\s+", " ", text).strip()          # collapse whitespace
    return text.lower()


def main() -> None:
    # -- 1. Check file exists ------------------------------------------------
    if not RAW_CSV.exists():
        print(
            f"\n[ERROR] File not found: {RAW_CSV}\n"
            "  The archive should be extracted at:\n"
            "  data/amazon_review_polarity_csv/train.csv\n"
        )
        sys.exit(1)

    # -- 2. Load (no header row) ---------------------------------------------
    print(f"[INFO] Loading {RAW_CSV.name} ...")
    df = pd.read_csv(
        RAW_CSV,
        header=None,
        names=["polarity", "title", "text"],
        low_memory=False,
    )
    print(f"       Raw shape: {df.shape}")

    # -- 3. Rename to standard schema ----------------------------------------
    # polarity: 1 = Negative (1-2 star reviews), 2 = Positive (4-5 star reviews)
    df.rename(columns={"text": "review_text", "title": "product_name"}, inplace=True)
    df["star_rating"] = df["polarity"]   # keep raw polarity label (1 or 2)
    df["source"]      = "amazon_kaggle"
    df["review_date"] = pd.NaT           # this dataset has no date column

    # -- 4. Sample -----------------------------------------------------------
    if SAMPLE_SIZE and len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=RANDOM_SEED).reset_index(drop=True)
        print(f"       Sampled to {SAMPLE_SIZE} rows.")

    # -- 5. Drop nulls & duplicates ------------------------------------------
    before = len(df)
    df.dropna(subset=["review_text"], inplace=True)
    df.drop_duplicates(subset=["review_text"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    after = len(df)
    print(f"       Dropped {before - after} null/duplicate rows -> {after} remaining.")

    # -- 6. Clean text -------------------------------------------------------
    print("[INFO] Cleaning text ...")
    tqdm.pandas(desc="       Cleaning")
    df["cleaned_text"] = df["review_text"].progress_apply(clean_text)

    # Drop rows where cleaning left an empty string
    df = df[df["cleaned_text"].str.strip().ne("")]
    df.reset_index(drop=True, inplace=True)

    # -- 7. Select & order final columns -------------------------------------
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")

    final_cols = [
        "source",
        "product_name",
        "review_text",
        "cleaned_text",
        "star_rating",
        "review_date",
    ]
    df = df[[c for c in final_cols if c in df.columns]]

    # -- 8. Save -------------------------------------------------------------
    CLEAN_OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CLEAN_OUT, index=False)
    print(f"\n[DONE] Saved {len(df)} rows -> {CLEAN_OUT}")
    print(f"\nSample output:\n{df.head(3).to_string()}\n")


if __name__ == "__main__":
    main()
