# TechManager 3.0 — A Tech Stack Recommendation System for Software Projects

TechManager 3.0 is an **explainable, rule-based decision-support web application** for early-stage software project planning.

It converts project requirements into a structured recommendation covering the technology stack, architecture, security controls, team roles and delivery roadmap.

> **Scope note:** TechManager is a PBL prototype. Its scores and recommendations are deterministic heuristics defined in the rule base; they are not statistical accuracy measurements and do not guarantee the universally optimal technology choice.


## v3.0 presentation-ready features

- Quick-start demo scenarios for Banking, Education and E-Commerce
- Recommendation comparison for 2–3 saved projects
- JSON export for every recommendation
- Dedicated comparison/decision-lab view
- Improved report toolbar for printing and export
- Responsive presentation-focused UI
- Existing recommendation history, search, filters, security checklist and roadmap retained

## What it considers

The current engine considers:

- Project type
- Team size
- Budget
- Expected users
- Security requirement
- Scalability need
- Team experience
- Delivery deadline

Supported project domains:

- Portfolio
- Education
- Hospital
- Banking
- E-Commerce
- E-Sports

## What it produces

- Frontend
- Backend
- Database
- Hosting
- Architecture
- Complexity level
- Scalability indicator
- Rule-fit score
- Development-time estimate
- Cost planning range
- Security checklist
- Additional tools
- Suggested team roles
- Delivery roadmap
- Alternative technologies
- Explainable decision summary

## Architecture

```text
Browser
   |
   v
HTML / CSS / JavaScript
   |
   v
Flask Web Application
   |
   +----> Rule Engine
   |        |
   |        +--> Stack rules
   |        +--> Architecture rules
   |        +--> Planning rules
   |        +--> Security rules
   |
   v
SQLite
   |
   v
History / Detailed Reports

Optional integration:
POST /api/recommend
```

## Engineering features

- Server-side input validation
- Parameterized SQL queries
- Automatic SQLite schema migration
- Explainable recommendation factors
- Deterministic rule engine
- JSON API endpoint
- Health endpoint
- Search and filtering
- Recommendation history
- Print-friendly report
- Responsive UI
- Automated unit/API tests

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

```text
http://127.0.0.1:5000
```

## Run tests

The project uses Python's built-in `unittest` framework:

```bash
python -m unittest discover -s tests -v
```

## API

### `GET /api`

Returns the API contract and supported fields.

### `POST /api/recommend`

Example:

```json
{
  "project_type": "Hospital",
  "team_size": 5,
  "budget": "High",
  "expected_users": "10,000–100,000",
  "security_level": "High",
  "scalability_need": "High",
  "team_experience": "Intermediate",
  "deadline": "Standard"
}
```

The endpoint returns the same explainable recommendation structure used by the web application.

## Deployment

For Render:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

The application initializes the database at import time so it works correctly under a WSGI server such as Gunicorn.

### Database note

SQLite is appropriate for the PBL prototype and simple deployments. For a production multi-user system requiring durable cloud persistence and concurrent writes, migrate to PostgreSQL or another managed database.

## Future engineering direction

1. Expert validation of the rule base
2. Larger project-domain coverage
3. Authentication and user workspaces
4. PostgreSQL
5. Historical-project feedback
6. Data-driven/hybrid recommendation models
7. Continuous technology metadata updates
8. CI/CD and production observability


## v3.1 feature: Similar Projects & Industry References

Each recommendation now includes curated public reference projects for the selected domain. For example, E-Commerce recommendations surface Amazon, Flipkart and Meesho; Education surfaces EngiNotes, Coursera and Khan Academy. These are learning/reference links only and are not presented as evidence of private architecture, performance, or technology choices.
