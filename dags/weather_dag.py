from airflow import DAG
from airflow.operators.python import PythonOperator
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
    extract_task