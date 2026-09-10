# System Architecture

Source dataset → ETL module → SQLite → SQL analytics → Streamlit app → Plotly visualizations.

Deployment: developer machine → Git → GitHub → Streamlit Cloud → public browser.

Trade-offs: SQLite is quick and explainable but not high-concurrency production infrastructure; Streamlit reduces frontend work but is less flexible than a dedicated web stack; precomputed analytics can improve responsiveness but reduce freshness.
