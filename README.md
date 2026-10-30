# HCL Python Assessment

Café sales notebook + a Streamlit dashboard. pandas, Plotly, Streamlit.

Filters on the left (outlet, item, month names, offer). The main page has the totals, five charts, and a download for the filtered rows.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

`app.py` reads `cafe_clean.csv` from this folder. The Jupyter notebook is the full walkthrough (cleaning, charts, HTML dashboards). It does **not** overwrite `app.py` if you re-run it.

## Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/ with GitHub.
2. Create an app from this repo / `main`.
3. Main file: `app.py`.
4. Keep `app.py`, `cafe_clean.csv`, and `requirements.txt` at the repo root.
