# Hospital Finder

A Streamlit emergency healthcare finder with hospital search, maps, blood-bank and pharmacy discovery, patient profiles, doctor consultations, appointment workflows, and role-based dashboards.

## Run locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

The application can use MongoDB through `MONGODB_URI` and `MONGODB_DATABASE` environment variables or Streamlit secrets. Never commit `.streamlit/secrets.toml`, credentials, or personal healthcare records.

The public repository includes only non-sensitive healthcare seed data. User accounts and consultation history are intentionally excluded from version control and should be created in a local or hosted database.

## Safety

This project is for demonstration and development purposes. It does not replace professional medical advice or emergency services. For life-threatening emergencies, contact local emergency services.
