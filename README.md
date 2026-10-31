# ABIT HostelCare

Hostel complaint management for Ajay Binay Institute of Technology.
Roles: Student, Warden, Admin.

## Run
    pip install -r requirements.txt
    python -m streamlit run app.py


## Set before the final demo
1. config.py: replace HOSTELS with the real ABIT hostel names; set SEED_DEMO_DATA = False for real use.
2. Secrets (see .streamlit/secrets.toml.example): SMTP_USER, SMTP_PASSWORD, ADMIN_PASSWORD.

## Structure
    app.py          login gate, role-based menu, hostel selector
    config.py       college name, hostels, authorised warden emails
    auth.py         login, sign up, admin/warden accounts
    database.py     SQLite tables and queries
    analytics.py    statistics and insights (pandas)
    charts.py       Altair charts
    notify.py       email to the assigned warden
    demo_data.py    sample data
    styles.py       CSS and HTML helpers
    views/          all pages
