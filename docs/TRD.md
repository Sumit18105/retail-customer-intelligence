# Technical Requirements / Design

Python + Pandas ETL → SQLite → SQL analytics → RFM → Streamlit/Plotly → public URL.

ETL standardizes columns/types, removes duplicates, validates IDs/dates/quantity/price, calculates revenue and loads relational tables. SQL performs core aggregations; Python orchestrates the application and visualization.

Indexes are added only for common joins/filter patterns. Query performance uses actual timings and `EXPLAIN QUERY PLAN`; no fixed gains are fabricated. SQLite is the MVP database with a documented migration path to PostgreSQL/warehouse systems.
