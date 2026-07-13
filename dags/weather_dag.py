from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from extractors.weather_extractor import run, notify_telegram
from airflow.models import Variable

def notify_failure(context):
    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id
    notify_telegram(f"FALHA na pipeline! DAG: {dag_id} | Task: {task_id}")

def send_success():
    token = Variable.get("TELEGRAM_TOKEN")
    chat_id = Variable.get("TELEGRAM_CHAT_ID")
    import requests
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                  data={"chat_id": chat_id, "text": "Pipeline executada com sucesso!"})

with DAG(
    dag_id="weather_extract",
    start_date=datetime(2026, 6, 28),
    schedule_interval="0 0 * * *",
    catchup=False,
    on_failure_callback=notify_failure
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

    notify_task = PythonOperator(
        task_id="notify_success",
        python_callable=send_success
    )

    extract_task >> dbt_silver_task >> dbt_gold_task >> notify_task