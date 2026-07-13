{{ config(
    materialized='table',
    partition_by={
      "field": "time_utc",
      "data_type": "timestamp",
      "granularity": "day"
    }
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'weather_raw') }}
),

deduplicated AS (
    SELECT *,
    ROW_NUMBER() OVER(
        PARTITION BY city, time
        ORDER BY extracted_at DESC
    ) AS rn
    FROM source
),

final AS (
    SELECT
        PARSE_TIMESTAMP('%Y-%m-%dT%H:%M', time) AS time_utc,
        city,
        CAST(temperature_2m AS FLOAT64)   AS temperature_2m,
        CAST(apparent_temperature AS FLOAT64) AS apparent_temperature,
        CAST(precipitation_probability AS INT64) AS precipitation_probability,
        CAST(precipitation AS FLOAT64)    AS precipitation,
        CAST(relative_humidity_2m AS INT64) AS relative_humidity_2m,
        CAST(uv_index AS FLOAT64)         AS uv_index,
        CAST(wind_speed_10m AS FLOAT64)   AS wind_speed_10m,
        CAST(wind_gusts_10m AS FLOAT64)   AS wind_gusts_10m,
        CAST(cloud_cover AS INT64)        AS cloud_cover,
        CAST(weather_code AS INT64)       AS weather_code,
        CAST(extracted_at AS TIMESTAMP)   AS extracted_at
    FROM deduplicated
    WHERE rn = 1
)

SELECT * FROM final