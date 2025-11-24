# CRM AI Control Tower (Einstein/Agentforce-inspired demo)

This Streamlit app demonstrates **strategic CRM decision making** using Einstein-style scores:

- **Churn Risk**
- **Customer Lifetime Value (CLV proxy)**
- **Upsell Potential**
- **Next-Best Action**
- **Retention Budget Optimizer**

## Files
- `streamlit_app.py` — main app
- `requirements.txt` — dependencies for Streamlit Cloud
- `sample_customers.csv` — example Customer 360 dataset

## Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy
1. Push these files to a GitHub repo.
2. Go to Streamlit Community Cloud → Create app → select repo and `streamlit_app.py`.
3. Add secrets only if you connect to Salesforce Einstein Prediction Service (optional).
