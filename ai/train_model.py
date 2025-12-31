import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import psycopg2

conn = psycopg2.connect(
    host="postgres",
    dbname="realtime_analytics",
    user="analytics",
    password="analytics"
)

df = pd.read_sql("SELECT * FROM revenue_per_minute", conn)

df["minute"] = pd.to_datetime(df["minute"])
df["x"] = range(len(df))

model = LinearRegression()
model.fit(df[["x"]], df["total_revenue"])

joblib.dump(model, "model.pkl")
