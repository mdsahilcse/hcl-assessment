# HCL Python Assessment

An executive-style café sales dashboard for 2025, with a friendly blue, pink, and gold palette. Five headline metrics summarize the selected view, and the main charts sit side by side for a quick read. Tabs keep deeper product, outlet, offer, and data analysis easy to reach. The page includes an original inline café illustration, a highest-month marker, readable value labels, detailed hover notes, filters, and CSV download.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app reads `cafe_clean.csv` from this folder. The Jupyter notebook is a guided walkthrough of the data checks, cleaning choices, charts, and interactive dashboard.

## Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/ with GitHub.
2. Choose **Create app**, then select `mdsahilcse/hcl-assessment` and the `main` branch.
3. Set the app file to `app.py` and deploy.
4. Keep `app.py`, `cafe_clean.csv`, and `requirements.txt` in the repository root.
