# HCL Python Assessment

A café sales explorer designed for both quick reading and hands-on investigation. The Streamlit app includes friendly filters, live summary numbers, month/week/day trends, outlet and product comparisons, offer analysis, weekday patterns, chart zoom and image export, and filtered CSV downloads. A short explanation beside each chart helps readers understand what they are seeing.

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
