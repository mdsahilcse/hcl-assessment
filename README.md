# HCL Python Assessment

A café sales explorer with a light blue, pink, and yellow palette. Charts are separated into tabs so you can focus on one question at a time: overall trends, products, outlets, offers, or the underlying data. The filters update the full view, and comparison controls switch between totals and averages. The app includes short plain-language explanations, a revenue distribution view, a reset button, and CSV download.

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
