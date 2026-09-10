# Retail Customer Intelligence & Campaign Analytics

A lightweight hosted retail analytics application that converts transaction data into customer segments, retention insights and campaign recommendations using Python, SQL, SQLite, RFM analysis and Streamlit.

> **Portfolio positioning:** This is an independently designed project inspired by real-world retail/customer-engagement problems. It is not an internal Xeno system and does not use proprietary Xeno data.

## Live Demo

`https://YOUR-APP.streamlit.app` — replace this placeholder after deployment.

## Business Question

**Which customers are most valuable, which customers are at risk, and which customer segments should a retailer prioritize for targeted engagement?**

## Features

- Executive sales and customer KPIs
- RFM customer segmentation
- At-risk and high-value customer identification
- Campaign recommendations
- Interactive filters
- SQL-backed analytics
- Indexing + `EXPLAIN QUERY PLAN` demonstration
- Streamlit deployment path

## Architecture

```text
CSV
 ↓
Python / Pandas ETL
 ↓
SQLite relational database
 ↓
SQL analytics
 ↓
RFM segmentation
 ↓
Streamlit + Plotly
 ↓
Public URL
```

The architecture intentionally stays compact for an MVP. The supporting technical specification uses SQLite, separates ETL/data access from application logic as practical, and treats SQL as the primary analytical interface. See the project TRD and architecture documents. fileciteturn0file1 fileciteturn0file2

## RFM Method

- **Recency:** days since the customer's most recent order relative to the dataset analysis date.
- **Frequency:** distinct order count.
- **Monetary:** total revenue.
- Each dimension is scored into quintiles and combined into reproducible heuristic segments. The rules are analytical heuristics, not industry-standard guarantees. This follows the SQL analytics specification. fileciteturn0file4

## SQL Optimization

The SQL Performance page compares a customer lookup before and after an index and displays `EXPLAIN QUERY PLAN`. It records actual local timings rather than claiming a fixed speed-up. On a small demo dataset, wall-clock differences may be negligible; the access-strategy change is the main teaching point. fileciteturn0file4

## Data

The repository includes deterministic demo data so the app works without a download step. For a public real-world source, use UCI Online Retail. UCI reports 541,909 transactions and a CC BY 4.0 license. urlUCI Online Retail datasethttps://archive.ics.uci.edu/dataset/352/online+retail

## Local Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python etl.py
streamlit run app.py
```

## Tests

```bash
pytest -q
```

## Project Structure

```text
app.py
etl.py
analytics.py
analytics.sql
requirements.txt
README.md
data/demo_retail_data.csv
database/retail.db
scripts/generate_demo_data.py
scripts/download_uci.py
tests/test_data.py
docs/
```

## Deployment

1. Push the folder to GitHub.
2. Keep paths relative; no local-machine dependencies.
3. In Streamlit Community Cloud, select the repository and `app.py` as the entry point.
4. Open the generated public URL in an incognito window and verify charts, filters, data and the SQL performance page.
5. Replace the README placeholder URL with the actual hosted URL. Do not invent one.

The deployment guide emphasizes a clean-browser check, no secrets, relative paths and a working `app.py` entry point. fileciteturn0file9

## Testing & Validation

The validation approach covers data quality, SQL reconciliation, join correctness, segment reconciliation, UI behavior and public deployment. fileciteturn0file7

## AI-Native Development

AI tools may assist with SQL drafts, Python debugging, test generation, documentation, dashboard layout and query-plan explanations. All generated suggestions must be executed and validated before inclusion; source-of-truth calculations remain in SQL/Python. fileciteturn0file5

## Limitations

- SQLite is a portfolio/demo database, not a production warehouse.
- The included demo dataset is synthetic; it is not real customer data.
- RFM segments are heuristic and should be validated against campaign outcomes.
- Performance measurements are environment-dependent.
- The app is batch-oriented rather than real-time.

## Future Improvements

- PostgreSQL or warehouse migration
- Scheduled ETL
- Campaign experiment tracking and uplift measurement
- Customer lifetime value
- Real-time customer events
- Optional SQL-backed natural-language “Ask Your Data” interface

## Interview Narrative

> I built a hosted retail customer intelligence application that uses Python and SQL to transform transaction data into RFM-based customer segments and campaign recommendations. I also added a query-performance section to demonstrate indexing and query-plan analysis. I intentionally scoped it as an MVP so the workflow could be deployed and validated end-to-end.
