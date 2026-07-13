from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from extractors.weather_extractor import run

with DAG(
    dag_id="weather_extract",
    start_date=datetime(2026, 6, 28),
    schedule_interval="0 0 * * *",
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id="weather_extract",
        python_callable=run
    )

    dbt_silver_task = BashOperator(
        task_id="dbt_silver",
        bash_command="cd /opt/airflow/weather_transform && /home/airflow/.local/bin/dbt run --select stg_weather"
    )
    
    dbt_gold_task = BashOperator(
        task_id="dbt_gold",
        bash_command="cd /opt/airflow/weather_transform && /home/airflow/.local/bin/dbt run --select agg_weather_daily"
    )

    extract_task >> dbt_silver_task >> dbt_gold_task