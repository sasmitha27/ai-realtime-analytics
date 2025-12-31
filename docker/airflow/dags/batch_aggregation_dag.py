from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime

with DAG(
    dag_id="daily_revenue_aggregation",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    aggregate = PostgresOperator(
        task_id="aggregate_revenue",
        postgres_conn_id="postgres_default",
        sql="""
        INSERT INTO revenue_per_minute
        SELECT date_trunc('minute', event_time), SUM(amount)
        FROM booking_events
        GROUP BY 1;
        """
    )
