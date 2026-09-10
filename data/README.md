# Dataset

The included `demo_retail_data.csv` is deterministic portfolio demo data generated with a fixed seed. It exists so the app runs locally and on Streamlit Community Cloud without external data dependencies.

For a public real-world retail source, use the UCI Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

UCI describes it as 541,909 transactions from a UK-based non-store online retailer covering 01/12/2010–09/12/2011 and licenses it under CC BY 4.0. Cite Chen (2015), UCI Machine Learning Repository, DOI 10.24432/C5BW33.

The schema adapter in `etl.py` expects a normalized CSV with the project columns. `scripts/download_uci.py` downloads the public workbook when network access is available; a production portfolio deployment should include only data permitted by the source license and repository size limits.
