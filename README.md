

# Cyber Ops Tracker (Flask + SQLite)

A lightweight internal-style **cybersecurity operations tracker** that helps teams stay organized by tracking **risks, tasks, incidents, and documentation review dates** in one place.

This project is designed to reflect real-world cybersecurity program support work (documentation, coordination, status reporting, and follow-ups).

---

## Features

### Dashboard
- Open risks count
- High/Critical risks count
- Overdue tasks count
- Open incidents count
- Documents with reviews due in the next 30 days

### Modules
- **Risk Register**: severity, owner, due date, status, notes
- **Task Tracker**: category, assignee, due date, priority, status, notes
- **Incident Log**: incident date, severity, impacted system, status, summary
- **Documentation Tracker**: type, owner, version, last updated, next review date

---

## Tech Stack
- **Python 3**
- **Flask**
- **SQLite**
- **Bootstrap 5**

---

## Run Locally

### 1) Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate

### 2) Install dependencies

pip install -r requirements.txt

### 3) Start the app

python app.py

### Open in your browser:
	•	http://127.0.0.1:5000



Project Structure

cyber-ops-tracker/
├── app.py
├── tracker.db              # created automatically after first run
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── risks.html
│   ├── tasks.html
│   ├── incidents.html
│   └── documents.html
└── static/
    └── style.css




Notes
	•	This is a portfolio/demo project running on Flask’s development server.
	•	Data is stored in a local SQLite database (tracker.db).
	•	If deployed publicly, a production server (like gunicorn) is recommended.

