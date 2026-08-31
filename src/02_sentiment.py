# -*- coding: utf-8 -*-
"""
02_sentiment.py
---------------
Step 3 of the pipeline:
  - Load the cleaned parquet produced by 01_preprocess.py
  - Run VADER sentiment analysis on each review
  - Bucket scores into Positive / Neutral / Negative labels
  - Export enriched parquet for the database loader

Usage:
    python src/02_sentiment.py

Input:
    data/reviews_clean.parquet

Output:
    data/reviews_scored.parquet
    data/sentiment_summary.csv   (distribution table)
"""

import io
import sys
import pathlib
import pandas as pd
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Force UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# -- Paths -------------------------------------------------------------------
ROOT        = pathlib.Path(__file__).resolve().parents[1]
CLEAN_IN    = ROOT / "data" / "reviews_clean.parquet"
SCORED_OUT  = ROOT / "data" / "reviews_scored.parquet"
SUMMARY_OUT = ROOT / "data" / "sentiment_summary.csv"


# -- VADER thresholds (industry standard) ------------------------------------
POS_THRESHOLD =  0.05
NEG_THRESHOLD = -0.05


def label_sentiment(compound: float) -> str:
    """Map VADER compound score -> human-readable label."""
    if compound >= POS_THRESHOLD:
        return "Positive"
    elif compound <= NEG_THRESHOLD:
        return "Negative"
    return "Neutral"


def score_review(analyzer: SentimentIntensityAnalyzer, text: str) -> dict:
    """Return full VADER scores dict for a single review string."""
    if not isinstance(text, str) or not text.strip():
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}
    return analyzer.polarity_scores(text)


def main() -> None:
    # -- 1. Load -------------------------------------------------------------
    if not CLEAN_IN.exists():
        print(
            f"\n[ERROR] File not found: {CLEAN_IN}\n"
            "  Run  python src/01_preprocess.py  first.\n"
        )
        sys.exit(1)

    print(f"[INFO] Loading {CLEAN_IN.name} ...")
    df = pd.read_parquet(CLEAN_IN)
    print(f"       Shape: {df.shape}")

    # -- 2. VADER scoring ----------------------------------------------------
    print("[INFO] Running VADER sentiment analysis ...")
    analyzer = SentimentIntensityAnalyzer()

    tqdm.pandas(desc="       Scoring")
    scores = df["cleaned_text"].progress_apply(
        lambda t: score_review(analyzer, t)
    )

    scores_df = pd.DataFrame(scores.tolist())
    df["vader_neg"]       = scores_df["neg"].round(4)
    df["vader_neu"]       = scores_df["neu"].round(4)
    df["vader_pos"]       = scores_df["pos"].round(4)
    df["sentiment_score"] = scores_df["compound"].round(4)  # the key metric

    # -- 3. Label ------------------------------------------------------------
    df["sentiment_label"] = df["sentiment_score"].apply(label_sentiment)

    # -- 4. Quick summary ----------------------------------------------------
    distribution = df["sentiment_label"].value_counts().reset_index()
    distribution.columns = ["sentiment_label", "count"]
    distribution["pct"] = (distribution["count"] / len(df) * 100).round(1)

    print("\n[INFO] Sentiment distribution:")
    print(distribution.to_string(index=False))

    avg_score = df["sentiment_score"].mean()
    print(f"\n       Overall avg compound score: {avg_score:.4f}")

    # -- 5. Save -------------------------------------------------------------
    df.to_parquet(SCORED_OUT, index=False)
    distribution.to_csv(SUMMARY_OUT, index=False)

    print(f"\n[DONE] Scored data  -> {SCORED_OUT}")
    print(f"[DONE] Summary CSV  -> {SUMMARY_OUT}")
    print(
        f"\nSample output:\n"
        f"{df[['review_text', 'sentiment_score', 'sentiment_label']].head(5).to_string()}\n"
    )


if __name__ == "__main__":
    main()
