import streamlit as st
import pandas as pd


@st.cache_resource
def get_db_conn():
    try:
        import psycopg2
    except Exception:
        st.error("psycopg2 is not installed. Install it with `pip install psycopg2-binary`.")
        return None

    try:
        conn = psycopg2.connect(
            dbname="hotel_analytics",
            user="airflow",
            password="airflow",
            host="localhost",
            port=5432,
        )
        return conn
    except Exception as e:
        st.error(f"Unable to connect to the database: {e}")
        return None


@st.cache_data(ttl=5)
def load_latest_revenue(conn, limit=50):
    if conn is None:
        return pd.DataFrame()
    try:
        df = pd.read_sql(
            "SELECT * FROM revenue_per_minute ORDER BY event_time DESC LIMIT %s",
            conn,
            params=(limit,),
        )
        if not df.empty and 'event_time' in df.columns:
            df['event_time'] = pd.to_datetime(df['event_time'])
        return df
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()


def main():
    st.title("Real-Time Analytics Dashboard")

    conn = get_db_conn()

    st.sidebar.header("Controls")
    limit = st.sidebar.slider("Rows to fetch", min_value=10, max_value=500, value=50, step=10)
    if st.sidebar.button("Refresh"):
        load_latest_revenue.clear()
        st.experimental_rerun()

    df = load_latest_revenue(conn, limit=limit)

    if df.empty:
        st.info("No data available to display.")
        return

    if 'revenue' not in df.columns:
        st.warning("Table does not contain a 'revenue' column.")
        st.dataframe(df)
        return

    chart_area = st.empty()
    with chart_area:
        st.line_chart(df.set_index('event_time')['revenue'].sort_index())


if __name__ == "__main__":
    main()
