# Real-Time Analytics Demo

This repository demonstrates a small real-time analytics stack using Kafka, Spark, Postgres, Airflow and a simple Python ML component. It contains utilities to produce events to Kafka, process them in Spark, persist aggregated data to Postgres, and a tiny ML training/prediction workflow.

---

## Project overview

- Purpose: Demonstrate an end-to-end lightweight streaming analytics pipeline with test scripts you can run locally.
- Components:
  - Event ingestion via Kafka.
  - Stream processing with Spark (example `spark/stream_processor.py`).
  - Batch aggregation DAG placeholder in Airflow (`airflow/dags`).
  - Persistent store in Postgres (Docker container in compose).
  - Simple ML training (`ai/train_model.py`) and prediction (`ai/predict.py`).

---

## File structure

Root layout (important files/folders):

- `ai/`
  - `train_model.py` — example script to train a LinearRegression model from Postgres data and save `model.pkl`.
  - `predict.py` — loads `model.pkl` (or uses a safe fallback) and prints a prediction.
- `airflow/dags/` — Airflow DAGs (placeholder files).
- `docker/docker-compose.yml` — Docker Compose for Kafka, Zookeeper, Postgres, Spark, Airflow and Metabase. Note: updated to advertise Kafka on localhost for host clients.
- `kafka/`
  - `producer.py` — continuous producer example.
  - `test_producer.py` — short producer that sends a few messages and exits.
  - `test_consumer.py` — short consumer that reads messages and exits.
  - `integration_test.py` — integration script that runs a consumer thread, produces N messages, and verifies roundtrip.
- `spark/stream_processor.py` — example Spark Structured Streaming job that reads from Kafka and aggregates revenue per minute.
- `warehouse/schema.sql` — database schema for Postgres.
- `requirements.txt` — Python dependencies for the project.

---

## Prerequisites

- Docker & Docker Compose (for Kafka, Zookeeper, Postgres, Spark, Airflow). Install from https://docs.docker.com.
- Python 3.8+ (recommended to use a virtual environment). The repo contains a `.venv` in this workspace — you can create one locally.

---

## Quick setup (local dev)

1. Create and activate a virtual environment, then install Python deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Start the required services (Kafka + Zookeeper + Postgres). From the project root:

```bash
docker compose -f docker/docker-compose.yml up -d zookeeper kafka postgres
```

Note: `docker/docker-compose.yml` has Kafka advertised on `localhost:9092` so host python clients can connect.

3. (Optional) Start other services from compose, e.g. Spark or Airflow, as needed:

```bash
docker compose -f docker/docker-compose.yml up -d spark airflow
```

---

## Running components

- Run the short producer to send a handful of test events:

```bash
.venv/bin/python kafka/test_producer.py
```

- Run the short consumer to read messages:

```bash
.venv/bin/python kafka/test_consumer.py
```

- Run the full integration test (consumer + producer + assertion):

```bash
.venv/bin/python kafka/integration_test.py
```

- Train the ML model (requires Postgres with data in `revenue_per_minute` table):

```bash
.venv/bin/python ai/train_model.py
```

- Predict using the saved model (reads `model.pkl` in the current working directory or uses a safe fallback):

```bash
.venv/bin/python ai/predict.py
```

Environment variable: set `MODEL_PATH` to point to a model file other than `model.pkl`.

---

## Integration notes & troubleshooting

- Kafka connectivity: If your producer/consumer cannot connect, ensure `kafka` container is up and `KAFKA_ADVERTISED_LISTENERS` in `docker/docker-compose.yml` is set to `PLAINTEXT://localhost:9092`.
- If you run into permission or network issues with Docker on macOS, ensure Docker Desktop is running and has required resources.
- Postgres: Compose exposes Postgres on port `5432`. If `ai/train_model.py` cannot connect, verify the DB is initialized and the `revenue_per_minute` table exists.
- Python packages: Install from `requirements.txt`. If a package fails to build (e.g., `pyspark`), consider installing it system-wide or using a pre-built image for Spark.

---

## Tests & CI suggestions

- Add a `Makefile` target or a small shell script that: (1) waits for Kafka readiness, (2) runs `kafka/integration_test.py`, and (3) tears down compose. This can run in CI with Docker-in-Docker.
- Example CI steps: start compose (Kafka + Zookeeper), run integration test, stop compose.

---

## Next steps

- Add a persistent Spark job that writes aggregated results to Postgres.
- Add real Airflow DAGs to schedule batch jobs and model retraining.
- Harden ML code with input validation and better model serialization.

---

## Detailed run commands (step-by-step)

Follow these exact steps to run the project locally on macOS (commands assume you're at the repository root):

1) Create and activate a virtual environment, then install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Start required Docker services (Zookeeper, Kafka, Postgres). This will also create containers for Spark, Airflow and Metabase but we focus on Kafka/Postgres/Spark here:

```bash
docker compose -f docker/docker-compose.yml up -d zookeeper kafka postgres
```

3) Verify services are healthy and listening (give Docker a few seconds to start):

```bash
docker compose -f docker/docker-compose.yml ps
docker logs docker-kafka-1 --tail 100
docker logs docker-postgres-1 --tail 100
```

4) (Optional) If you want Spark running inside the container (recommended to avoid installing Java locally), start the Spark container and run the streaming job there. First ensure the spark service is up and the repo is mounted (the compose file mounts the repo into the container at `/opt/app`):

```bash
docker compose -f docker/docker-compose.yml up -d spark
docker ps --filter name=docker-spark-1
```

5) Run the Spark structured streaming job inside the Spark container (this uses Spark's Kafka connector which will be downloaded into a writable temporary Ivy cache inside the container). This command runs in the container and prints windowed aggregates to the container console:

```bash
docker exec -e KAFKA_BOOTSTRAP=kafka:9092 -it docker-spark-1 \
  /opt/spark/bin/spark-submit --master 'local[*]' \
  --conf 'spark.jars.ivy=/tmp/.ivy2' \
  --packages 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0' \
  /opt/app/spark/stream_processor.py
```

Notes:
- Use `KAFKA_BOOTSTRAP=kafka:9092` when running inside the container so Spark connects to the Kafka service on the Docker network.
- Quoting `local[*]` prevents shell globbing on macOS zsh.

6) In a separate terminal (with the same `.venv` activated), send test messages to Kafka to exercise the pipeline:

```bash
.venv/bin/python kafka/test_producer.py
```

7) You can also run the consumer locally to inspect messages directly from the topic:

```bash
.venv/bin/python kafka/test_consumer.py
```

8) Run the integration test (producer + consumer + assertion) from the workspace to validate message roundtrip:

```bash
.venv/bin/python kafka/integration_test.py
```

9) Train the ML model (requires a populated Postgres table `revenue_per_minute`):

```bash
.venv/bin/python ai/train_model.py
```

This will produce a `model.pkl` in the working directory — move or copy it to `ai/` or set `MODEL_PATH` before running prediction.

10) Run prediction:

```bash
MODEL_PATH=ai/model.pkl .venv/bin/python ai/predict.py
```

11) Stop and remove running containers when finished:

```bash
docker compose -f docker/docker-compose.yml down --volumes
```

Troubleshooting and tips:
- If Spark can't find the Kafka source, ensure you included the `--packages` flag for `spark-sql-kafka-0-10` and used a writable Ivy cache (`--conf 'spark.jars.ivy=/tmp/.ivy2'`).
- If you prefer running Spark locally on your host (not in Docker), install a JDK (OpenJDK 11 or 17) and ensure `SPARK_HOME`/`pyspark` are configured — otherwise containerized Spark avoids host Java setup.
- If Postgres has no data, `ai/train_model.py` will fail; seed the `revenue_per_minute` table using `warehouse/schema.sql` and sample data.