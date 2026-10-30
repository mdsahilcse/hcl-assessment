# HCL Python Assessment

Interactive café sales exploration and dashboard built with pandas, Plotly, and Streamlit.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app reads `cafe_clean.csv` from this folder. The Jupyter notebook contains the full analysis and can export the dashboard assets and Streamlit app.

## Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/ with GitHub.
2. Choose **Create app** and select this repository and its `main` branch.
3. Set the app file to `app.py`, then deploy.
4. Keep `app.py`, `cafe_clean.csv`, and `requirements.txt` in the repository root.
