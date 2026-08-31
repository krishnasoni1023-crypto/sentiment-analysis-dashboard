-- ─────────────────────────────────────────────────────────────────────────────
--  04_sql_queries.sql
--  Analytical queries for the Sentiment Analysis Dashboard
--  Database: sentiment_db   Table: reviews   (PostgreSQL syntax)
--
--  Connect first:  \c sentiment_db   (in psql)
--  Or select the database in pgAdmin before running.
-- ─────────────────────────────────────────────────────────────────────────────


-- ─────────────────────────────────────────────────────────────────────────────
-- Q1.  SENTIMENT DISTRIBUTION
--      How many reviews fall into each sentiment bucket?
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    sentiment_label,
    COUNT(*)                                                        AS review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1)              AS pct
FROM reviews
GROUP BY sentiment_label
ORDER BY review_count DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q2.  SENTIMENT TREND OVER TIME
--      Average compound score per day
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    review_date,
    COUNT(*)                            AS review_count,
    ROUND(AVG(sentiment_score)::NUMERIC, 4)  AS avg_compound,
    ROUND(AVG(vader_pos)::NUMERIC, 4)        AS avg_positive,
    ROUND(AVG(vader_neg)::NUMERIC, 4)        AS avg_negative
FROM reviews
WHERE review_date IS NOT NULL
GROUP BY review_date
ORDER BY review_date;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q3.  TOP 10 MOST POSITIVE REVIEWS
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    review_id,
    product_name,
    sentiment_score,
    LEFT(review_text, 300) AS review_snippet
FROM reviews
ORDER BY sentiment_score DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q4.  TOP 10 MOST NEGATIVE REVIEWS
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    review_id,
    product_name,
    sentiment_score,
    LEFT(review_text, 300) AS review_snippet
FROM reviews
ORDER BY sentiment_score ASC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q5.  SENTIMENT BREAKDOWN BY PRODUCT
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    product_name,
    sentiment_label,
    COUNT(*) AS cnt
FROM reviews
GROUP BY product_name, sentiment_label
ORDER BY product_name, sentiment_label;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q6.  OVERALL STATISTICS  (KPI cards in Power BI)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                                             AS total_reviews,
    ROUND(AVG(sentiment_score)::NUMERIC, 4)                             AS avg_compound_score,
    ROUND(AVG(star_rating)::NUMERIC, 2)                                 AS avg_star_rating,
    COUNT(*) FILTER (WHERE sentiment_label = 'Positive')                AS positive_count,
    COUNT(*) FILTER (WHERE sentiment_label = 'Neutral')                 AS neutral_count,
    COUNT(*) FILTER (WHERE sentiment_label = 'Negative')                AS negative_count,
    ROUND(COUNT(*) FILTER (WHERE sentiment_label = 'Positive') * 100.0 / COUNT(*), 1) AS positive_pct,
    ROUND(COUNT(*) FILTER (WHERE sentiment_label = 'Negative') * 100.0 / COUNT(*), 1) AS negative_pct
FROM reviews;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q7.  STAR RATING vs SENTIMENT LABEL
--      Validation: do VADER labels align with the polarity labels?
--      (star_rating: 1 = negative polarity, 2 = positive polarity)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    star_rating,
    sentiment_label,
    COUNT(*)                                    AS cnt,
    ROUND(AVG(sentiment_score)::NUMERIC, 4)     AS avg_score
FROM reviews
WHERE star_rating IS NOT NULL
GROUP BY star_rating, sentiment_label
ORDER BY star_rating, sentiment_label;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q8.  MONTHLY SENTIMENT AGGREGATION
--      (PostgreSQL uses TO_CHAR instead of DATE_FORMAT)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    TO_CHAR(review_date, 'YYYY-MM')                                      AS year_month,
    COUNT(*)                                                             AS review_count,
    ROUND(AVG(sentiment_score)::NUMERIC, 4)                             AS avg_compound,
    COUNT(*) FILTER (WHERE sentiment_label = 'Positive')                AS positive,
    COUNT(*) FILTER (WHERE sentiment_label = 'Neutral')                 AS neutral,
    COUNT(*) FILTER (WHERE sentiment_label = 'Negative')                AS negative
FROM reviews
WHERE review_date IS NOT NULL
GROUP BY year_month
ORDER BY year_month;
