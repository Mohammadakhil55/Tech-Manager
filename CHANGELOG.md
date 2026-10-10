# Changelog

## 3.1.0
- Added domain-aware Similar Projects & Industry References cards.
- Added curated official website links for Portfolio, Education, Hospital, Banking, E-Commerce and E-Sports.
- Added reference explanations so users understand why each example is relevant.
- Fixed dashboard recent-analysis data binding.
- Preserved the deterministic rule engine and existing v3.0 functionality.

# TechManager 3.0 — Release Notes

## Added
- Presentation Mode quick-start scenarios.
- Decision Lab comparison for 2–3 saved recommendations.
- JSON report export endpoint: `/export/<id>.json`.
- Recommendation comparison route: `/compare?ids=1&ids=2`.
- Improved client-side validation for compare selection.
- Versioned UI footer and release identity.

## Preserved
- Deterministic rule engine.
- Eight recommendation factors.
- Six supported domains.
- Recommendation history and filtering.
- Security checklist, team roles and delivery roadmap.
- REST-style JSON API and health endpoint.
- SQLite persistence and existing test suite.

## Run
Windows:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000
