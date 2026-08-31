SELECT
    star_rating,
    sentiment_label,
    COUNT(*) AS cnt,
    ROUND(AVG(sentiment_score)::NUMERIC, 4) AS avg_score
FROM reviews
GROUP BY star_rating, sentiment_label
ORDER BY star_rating, sentiment_label;
