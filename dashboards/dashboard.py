import streamlit as st
import pandas as pd
import psycopg2
import time

# DB connection
conn = psycopg2.connect(
    dbname="hotel_analytics",
    user="airflow",
    password="airflow",
    host="localhost",
    port=5432
)

st.title("Real-Time Analytics Dashboard")

while True:
    df = pd.read_sql("SELECT * FROM revenue_per_minute ORDER BY event_time DESC LIMIT 50", conn)
    st.line_chart(df.set_index('event_time')['revenue'])
    time.sleep(5)  # refresh every 5 seconds
