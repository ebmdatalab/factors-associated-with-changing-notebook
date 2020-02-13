WITH practice_numerator AS (
    SELECT
        CAST(month AS DATE) AS month,
        practice AS practice_id,
        {numerator_columns}
    FROM {numerator_from}
    WHERE {numerator_where}
    GROUP BY month, practice_id
),

practice_denominator AS (
    SELECT
        CAST(month AS DATE) AS month,
        practice AS practice_id,
        {denominator_columns}
    FROM {denominator_from}
    WHERE {denominator_where}
    GROUP BY month, practice_id
),

month_practice AS (
    SELECT
        m.month,
        p.id AS practice_id
    FROM public_draft.practice AS p
    CROSS JOIN (
        SELECT DISTINCT month FROM practice_numerator
        UNION DISTINCT
        SELECT DISTINCT month FROM practice_denominator
        ORDER BY month
    ) AS m
    WHERE p.setting = 4
),

practice_combined AS (
    SELECT
        mp.month,
        mp.practice_id,
        COALESCE(n.numerator, 0) AS numerator,
        COALESCE(d.denominator, 0) AS denominator
    FROM month_practice AS mp
    LEFT JOIN practice_numerator AS n
        ON mp.month = n.month AND mp.practice_id = n.practice_id
    LEFT JOIN practice_denominator AS d
        ON mp.month = d.month AND mp.practice_id = d.practice_id
),

practice_combined_with_ratio AS (
    SELECT
        month,
        practice_id,
        numerator,
        denominator,
        CASE
            WHEN numerator = 0 AND denominator = 0 THEN 0
            WHEN denominator = 0 THEN NULL
            ELSE numerator / denominator
        END AS ratio
    FROM practice_combined
)

SELECT
    *,
    PERCENT_RANK() OVER (PARTITION BY month ORDER BY ratio) AS percentile
FROM practice_combined_with_ratio
ORDER BY month DESC, percentile DESC
