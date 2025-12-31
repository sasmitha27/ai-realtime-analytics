CREATE TABLE IF NOT EXISTS booking_events (
    event_id UUID PRIMARY KEY,
    user_id INT,
    hotel_id INT,
    amount NUMERIC,
    event_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS revenue_per_minute (
    minute TIMESTAMP PRIMARY KEY,
    total_revenue NUMERIC
);
