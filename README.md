# SQL Injection Demo — SecureBank

## Project Structure
```
sql-injection-demo/
├── database/
│   ├── init_db.py       ← Seeds SQLite with fake users, accounts, secrets
│   └── bank.db          ← Created after running init_db.py
├── flask_app/
│   ├── app.py           ← Flask routes (vulnerable + secure)
│   └── templates/
│       ├── login.html   ← Fake bank login page
│       └── dashboard.html
├── streamlit_app/
│   └── dashboard.py     ← Live DB viewer + attack simulator
├── requirements.txt
├── start_demo.sh        ← Starts both servers
└── README.md
```

## Quick Start
```bash
pip install -r requirements.txt
python database/init_db.py
# Terminal 1:
cd flask_app && python app.py
# Terminal 2:
streamlit run streamlit_app/dashboard.py
```

## Demo URLs
- Vulnerable Login:  http://localhost:5000/login
- Secure Login:      http://localhost:5000/secure-login
- Hacker Console:    http://localhost:8501
- Reset Database:    http://localhost:5000/reset-db

## Attack Payloads
| Field    | Payload           | Effect              |
|----------|-------------------|---------------------|
| Password | ' OR '1'='1       | Bypass password     |
| Username | ' OR 1=1 --       | Bypass both checks  |
| Password | ' OR '1'='1' --   | Comment injection   |
