[README.md](https://github.com/user-attachments/files/31654450/README.md)
# 📊 Sentiment Analysis Dashboard

> End-to-end NLP pipeline: Amazon reviews → VADER sentiment → PostgreSQL → Power BI

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![VADER](https://img.shields.io/badge/NLP-VADER%20Sentiment-orange)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Visualization-Power%20BI-F2C811?logo=powerbi&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Problem Statement

Online reviews are a goldmine of customer feedback, but reading thousands of
them manually is infeasible. This project automates sentiment classification at
scale, stores the results in a relational database, and surfaces actionable
insights through an interactive Power BI dashboard.

---

## Architecture

```
Kaggle CSV
    │
    ▼
01_preprocess.py   ─── clean text (regex, lowercasing) ──► reviews_clean.parquet
    │
    ▼
02_sentiment.py    ─── VADER scoring + label bucketing ──► reviews_scored.parquet
    │
    ▼
03_load_mysql.py   ─── SQLAlchemy bulk insert ───────────► MySQL (sentiment_db)
    │
    ▼
04_sql_queries.sql ─── analytical views / aggregations
    │
    ▼
Power BI Desktop   ─── live MySQL connection → dashboard
```

---

## Dataset

| Field | Details |
|---|---|
| Source | [Amazon Reviews — Kaggle](https://www.kaggle.com/datasets/kritanjalijain/amazon-reviews) |
| Rows used | 2 000 (random sample) |
| Key columns | `reviewText`, `overall` (star rating), `asin` (product ID), `reviewTime` |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| Data wrangling | Pandas |
| NLP / Sentiment | VADER (vaderSentiment) |
| Database | MySQL 8.x |
| ORM / loader | SQLAlchemy + PyMySQL |
| Visualization | Power BI Desktop |

---

## Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/sentiment-analysis-dashboard.git
cd sentiment-analysis-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the dataset

Download **`train.csv`** from the Kaggle link above and place it at:

```
data/reviews_raw.csv
```

### 4. Configure MySQL credentials

Edit `config.py` (already gitignored):

```python
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_USER     = "root"
DB_PASSWORD = "your_password"
DB_NAME     = "sentiment_db"
```

### 5. Run the pipeline

```bash
# Step 1 — Preprocess
python src/01_preprocess.py

# Step 2 — Sentiment scoring
python src/02_sentiment.py

# Step 3 — Load to MySQL
python src/03_load_mysql.py
```

### 6. Run analytical queries

Open `src/04_sql_queries.sql` in MySQL Workbench and execute.

### 7. Connect Power BI

See [`dashboard/README_powerbi.md`](dashboard/README_powerbi.md) for the
step-by-step connection and visual setup guide.

---

## Key Insights

- **71% Positive reviews** (1,418 / 2,000) — the majority of Amazon customers express satisfaction
- **25.6% Negative reviews** (511 / 2,000) — common themes include product quality and unmet expectations
- **3.5% Neutral reviews** (71 / 2,000) — mixed or factual reviews with no strong sentiment signal
- **Average VADER compound score: +0.23** — overall net positive sentiment across the dataset
- **VADER accuracy validated**: reviews with polarity label `1` (negative star ratings) scored avg **-0.54**; polarity `2` (positive) scored avg **+0.75** — strong alignment confirms the model is working correctly


---

## Dashboard Preview

> *(Add a screenshot of your Power BI dashboard here)*

---

## Resume Bullet Points

- Built an end-to-end NLP pipeline in Python that classified **2,000 Amazon reviews** using VADER sentiment analysis, producing a distribution of **71% Positive / 3.5% Neutral / 25.6% Negative** with an average compound score of +0.23.
- Automated text cleaning (HTML stripping, regex normalization, stopword removal) and bulk-loaded enriched data into **PostgreSQL** via SQLAlchemy, reducing manual analysis time to near-zero.
- Validated model accuracy against ground-truth polarity labels: negative-rated reviews averaged a VADER score of **-0.54** and positive-rated reviews averaged **+0.75**, confirming strong alignment.
- Designed an interactive **Power BI dashboard** with 6 visuals (KPI cards, donut chart, bar chart, negative-review table, and slicers), enabling stakeholders to filter by sentiment label and star rating in real time.

---

## Project Structure

```
sentiment-analysis-dashboard/
├── data/                        # Raw + processed data (gitignored)
├── src/
│   ├── 01_preprocess.py         # Text cleaning pipeline
│   ├── 02_sentiment.py          # VADER sentiment scoring
│   ├── 03_load_mysql.py         # MySQL bulk loader
│   └── 04_sql_queries.sql       # Analytical SQL
├── dashboard/
│   └── README_powerbi.md        # Power BI connection guide
├── config.py                    # DB credentials (gitignored)
├── requirements.txt
└── README.md
```

---

## License

MIT — free to use, modify, and distribute.

pandas>=2.0
pyarrow>=14.0
vaderSentiment>=3.3.2
SQLAlchemy>=2.0
psycopg2-binary>=2.9
python-dotenv>=1.0
nltk>=3.8
tqdm>=4.66
