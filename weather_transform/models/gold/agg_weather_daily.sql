{{ config(
    materialized='table',
    partition_by={
      "field": "date_utc",
      "data_type": "date",
      "granularity": "day"
    }
) }}

WITH silver AS (
    SELECT * FROM {{ ref('stg_weather') }}
),

final AS (
    SELECT
        DATE(time_utc)                        AS date_utc,
        city,
        ROUND(AVG(temperature_2m), 2)         AS avg_temperature,
        ROUND(MAX(temperature_2m), 2)         AS max_temperature,
        ROUND(MIN(temperature_2m), 2)         AS min_temperature,
        ROUND(AVG(apparent_temperature), 2)   AS avg_apparent_temperature,
        ROUND(SUM(precipitation), 2)          AS total_precipitation_mm,
        ROUND(AVG(relative_humidity_2m), 2)   AS avg_humidity,
        ROUND(MAX(uv_index), 2)               AS max_uv_index,
        ROUND(AVG(wind_speed_10m), 2)         AS avg_wind_speed,
        ROUND(MAX(wind_gusts_10m), 2)         AS max_wind_gusts,
        ROUND(AVG(cloud_cover), 2)            AS avg_cloud_cover
    FROM silver
    GROUP BY DATE(time_utc), city
)

SELECT * FROM final