# TechManager

TechManager is a Flask-based rule-driven project technology recommendation system.

## Features

- Project technology-stack recommendation
- Architecture recommendation
- Complexity analysis
- Scalability score
- Estimated development time
- Budget range
- Security checklist
- Team-role recommendation
- Development roadmap
- Recommendation history
- Search and filtering
- Detailed report view
- Responsive UI
- SQLite database with automatic schema migration
- Render deployment configuration

## Local setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## Deploy on Render

Push this project to GitHub.

On Render choose:

- New → Web Service
- Connect the GitHub repository
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Plan: Free for a demonstration

Render will provide an `onrender.com` URL.

### Important database note

This project uses SQLite for easy local PBL demonstration. On a cloud platform, SQLite is suitable for a demo but is not the right choice when you need durable multi-user production data. For persistent team history, migrate the database to PostgreSQL.

## Health check

`/health` returns a simple JSON health response.
