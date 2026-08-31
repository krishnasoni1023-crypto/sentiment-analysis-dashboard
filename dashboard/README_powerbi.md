# Power BI — Connecting to MySQL & Building the Dashboard

## Prerequisites

| Requirement | Link |
|---|---|
| Power BI Desktop (free) | https://powerbi.microsoft.com/desktop |
| MySQL Connector/NET (required by Power BI) | https://dev.mysql.com/downloads/connector/net/ |

Install **MySQL Connector/NET** before opening Power BI. Choose the 64-bit
`.msi` installer that matches your Windows architecture.

---

## Step 1 — Connect Power BI to MySQL

1. Open **Power BI Desktop**.
2. Click **Home → Get Data → More…**
3. Search for **MySQL database** and click **Connect**.
4. Enter:
   - **Server**: `localhost` (or your Docker host IP)
   - **Database**: `sentiment_db`
5. Choose **Import** mode (recommended for dashboards under ~100 k rows).
6. Enter your MySQL username and password when prompted.
7. In the Navigator, tick the **`reviews`** table → **Load**.

---

## Step 2 — Recommended Visuals

### 2a. KPI Cards (top row)
- **Total Reviews** → Count of `review_id`
- **Avg Compound Score** → Average of `sentiment_score`
- **Positive %** → % of rows where `sentiment_label = "Positive"`
- **Negative %** → % of rows where `sentiment_label = "Negative"`

### 2b. Donut Chart — Sentiment Distribution
- **Legend**: `sentiment_label`
- **Values**: Count of `review_id`

### 2c. Line Chart — Sentiment Trend Over Time
- **X-Axis**: `review_date` (set hierarchy to Date)
- **Y-Axis**: Average of `sentiment_score`

### 2d. Clustered Bar Chart — Sentiment by Product
- **Y-Axis**: `product_name`
- **X-Axis**: Count of `review_id`
- **Legend**: `sentiment_label`

### 2e. Table — Top Negative Reviews
- Columns: `product_name`, `sentiment_score`, `review_text`
- Filter: `sentiment_label = "Negative"`
- Sort: `sentiment_score` ascending

### 2f. Gauge — Average Compound Score
- **Value**: Average `sentiment_score`
- **Min**: -1  **Max**: 1  **Target**: 0.05 (positive threshold)

---

## Step 3 — Slicers / Filters

Add these slicers to the top of the report page:

| Slicer | Field |
|---|---|
| Date range | `review_date` |
| Sentiment label | `sentiment_label` |
| Product | `product_name` |

---

## Step 4 — Color Theme (recommended)

Use a **3-color diverging palette** for sentiment:

| Label | Hex |
|---|---|
| Positive | `#2ECC71` |
| Neutral  | `#95A5A6` |
| Negative | `#E74C3C` |

Apply via **View → Themes → Customize current theme**.

---

## Step 5 — Publish (optional)

1. **File → Publish → Publish to Power BI** (requires a free Power BI account).
2. Share the workspace link with your team or embed it in your GitHub README.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| "MySQL Connector not found" | Install MySQL Connector/NET and restart Power BI |
| Authentication error | Double-check `config.py` credentials and MySQL user privileges |
| No data / empty table | Run `python src/03_load_mysql.py` first, verify row count |
| Date axis shows numbers | Change the `review_date` column data type to **Date** in Power Query |
