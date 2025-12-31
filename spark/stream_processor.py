import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, to_timestamp
from pyspark.sql.types import *

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")

spark = SparkSession.builder \
    .appName("RealTimeAnalytics") \
    .master("local[*]") \
    .getOrCreate()

schema = StructType([
    StructField("event_id", StringType()),
    StructField("user_id", IntegerType()),
    StructField("hotel_id", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("event_time", StringType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", "booking-events") \
    .load()

parsed = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Convert event_time string to timestamp for proper windowing
parsed = parsed.withColumn("event_ts", to_timestamp(col("event_time")))

agg = parsed \
    .withWatermark("event_ts", "1 minute") \
    .groupBy(window(col("event_ts"), "1 minute")) \
    .sum("amount")

query = agg.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
