# -*- coding: utf-8 -*-
"""
03_load_postgres.py
-------------------
Step 4 of the pipeline:
  - Read config.py for DB credentials
  - Create the PostgreSQL database + table if they don't exist
  - Load the scored parquet produced by 02_sentiment.py
  - Push all rows into PostgreSQL using SQLAlchemy / pandas .to_sql()
  - Verify the row count in the DB

Usage:
    python src/03_load_mysql.py

Input:
    data/reviews_scored.parquet
    config.py  (credentials -- gitignored)

Output:
    PostgreSQL table: sentiment_db.public.reviews
"""

import io
import sys
import pathlib
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text

# Force UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# -- Paths -------------------------------------------------------------------
ROOT      = pathlib.Path(__file__).resolve().parents[1]
SCORED_IN = ROOT / "data" / "reviews_scored.parquet"

# -- Import credentials ------------------------------------------------------
sys.path.insert(0, str(ROOT))
try:
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
except ImportError:
    print(
        "\n[ERROR] config.py not found.\n"
        "  Edit config.py in the project root with your PostgreSQL credentials.\n"
    )
    sys.exit(1)


# -- SQL: table definition (PostgreSQL syntax) --------------------------------
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reviews (
    review_id       SERIAL          PRIMARY KEY,
    source          VARCHAR(50)     NOT NULL DEFAULT 'amazon_kaggle',
    product_name    VARCHAR(255),
    review_text     TEXT,
    cleaned_text    TEXT,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(10),
    vader_neg       FLOAT,
    vader_neu       FLOAT,
    vader_pos       FLOAT,
    star_rating     FLOAT,
    review_date     DATE,
    inserted_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);
"""


def build_engine(db_name: str) -> sa.Engine:
    """Return a SQLAlchemy engine for the given database."""
    url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{db_name}"
    )
    return sa.create_engine(url, echo=False, isolation_level="AUTOCOMMIT")


def ensure_database() -> None:
    """Create the target database if it doesn't exist (connect via 'postgres' default DB)."""
    engine = build_engine("postgres")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": DB_NAME}
        ).fetchone()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
            print(f"    Created database '{DB_NAME}'.")
        else:
            print(f"    Database '{DB_NAME}' already exists.")
    engine.dispose()


def ensure_table(engine: sa.Engine) -> None:
    """Create the reviews table if it doesn't exist."""
    with engine.connect() as conn:
        conn.execute(text(CREATE_TABLE_SQL))
        conn.commit()
    print(f"    Table 'reviews' ready.")


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Align DataFrame columns to the DB schema."""
    col_map = {
        "review_text":     "review_text",
        "cleaned_text":    "cleaned_text",
        "sentiment_score": "sentiment_score",
        "sentiment_label": "sentiment_label",
        "vader_neg":       "vader_neg",
        "vader_neu":       "vader_neu",
        "vader_pos":       "vader_pos",
        "product_name":    "product_name",
        "star_rating":     "star_rating",
        "review_date":     "review_date",
        "source":          "source",
    }
    available = {k: v for k, v in col_map.items() if k in df.columns}
    out = df[list(available.keys())].rename(columns=available)

    # Coerce date column
    if "review_date" in out.columns:
        out["review_date"] = pd.to_datetime(out["review_date"], errors="coerce").dt.date

    # Trim long strings to stay within VARCHAR limits
    if "product_name" in out.columns:
        out["product_name"] = out["product_name"].astype(str).str[:255]
    if "source" in out.columns:
        out["source"] = out["source"].astype(str).str[:50]
    if "sentiment_label" in out.columns:
        out["sentiment_label"] = out["sentiment_label"].astype(str).str[:10]

    return out


def main() -> None:
    # -- 1. Load scored data -------------------------------------------------
    if not SCORED_IN.exists():
        print(
            f"\n[ERROR] File not found: {SCORED_IN}\n"
            "  Run  python src/02_sentiment.py  first.\n"
        )
        sys.exit(1)

    print(f"[INFO] Loading {SCORED_IN.name} ...")
    df_raw = pd.read_parquet(SCORED_IN)
    print(f"       Rows to insert: {len(df_raw)}")

    df = prepare_dataframe(df_raw)
    print(f"       Columns mapped: {list(df.columns)}")

    # -- 2. Create DB if needed ----------------------------------------------
    print(f"\n[INFO] Connecting to PostgreSQL at {DB_HOST}:{DB_PORT} ...")
    try:
        ensure_database()
    except Exception as exc:
        print(f"\n[ERROR] Could not connect to PostgreSQL:\n  {exc}\n")
        print(
            "  Checklist:\n"
            "  1. Is PostgreSQL running? (check Services or pgAdmin)\n"
            "  2. Are your config.py credentials correct?\n"
            "  3. Is port 5432 open?\n"
        )
        sys.exit(1)

    # -- 3. Connect to target DB and create table ----------------------------
    db_engine = build_engine(DB_NAME)
    ensure_table(db_engine)

    # -- 4. Push data --------------------------------------------------------
    print(f"\n[INFO] Inserting {len(df)} rows into '{DB_NAME}'.reviews ...")
    df.to_sql(
        name      = "reviews",
        con       = db_engine,
        if_exists = "append",   # append so re-runs don't wipe existing data
        index     = False,
        chunksize = 500,
        method    = "multi",
    )

    # -- 5. Verify -----------------------------------------------------------
    with db_engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM reviews")).scalar()

    print(f"\n[DONE] Insert complete. Total rows in DB: {total}")
    db_engine.dispose()


if __name__ == "__main__":
    main()
