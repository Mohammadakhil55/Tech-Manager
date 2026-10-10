from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
APP_VERSION = "3.1.0"
BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("TECHMANAGER_DB", BASE_DIR / "database.db"))


# -----------------------------
# Database helpers
# -----------------------------
SCHEMA = {
    "project_name": "TEXT NOT NULL",
    "project_type": "TEXT NOT NULL",
    "team_size": "INTEGER NOT NULL DEFAULT 1",
    "budget": "TEXT NOT NULL",
    "expected_users": "TEXT NOT NULL DEFAULT '<1,000'",
    "security_level": "TEXT NOT NULL DEFAULT 'Medium'",
    "scalability_need": "TEXT NOT NULL DEFAULT 'Medium'",
    "team_experience": "TEXT NOT NULL DEFAULT 'Intermediate'",
    "deadline": "TEXT NOT NULL DEFAULT 'Standard'",
    "complexity": "TEXT NOT NULL",
    "frontend": "TEXT NOT NULL",
    "backend": "TEXT NOT NULL",
    "database_name": "TEXT NOT NULL",
    "hosting": "TEXT NOT NULL",
    "architecture": "TEXT NOT NULL",
    "scalability": "INTEGER NOT NULL DEFAULT 0",
    "rule_fit_score": "INTEGER NOT NULL DEFAULT 0",
    "development_time": "TEXT NOT NULL",
    "estimated_cost": "TEXT NOT NULL",
    "decision_summary": "TEXT NOT NULL DEFAULT ''",
    "factors_json": "TEXT NOT NULL DEFAULT '{}'",
    "created_at": "TEXT NOT NULL"
}


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def row_to_recommendation(record):
    """Rebuild a recommendation from a saved record for exports/API/compare views."""
    return generate_recommendation(
        record["project_type"], record["team_size"], record["budget"],
        record["expected_users"], record["security_level"],
        record["scalability_need"], record["team_experience"],
        record["deadline"]
    )


def serialize_record(record):
    rec = row_to_recommendation(record)
    return {
        "id": record["id"],
        "project_name": record["project_name"],
        "created_at": record["created_at"],
        "inputs": rec["factors"],
        "recommendation": {
            "frontend": rec["frontend"], "backend": rec["backend"],
            "database": rec["database"], "hosting": rec["hosting"],
            "architecture": rec["architecture"], "complexity": rec["complexity"],
            "scalability": rec["scalability"], "rule_fit_score": rec["rule_fit_score"],
            "development_time": rec["development_time"], "estimated_cost": rec["estimated_cost"],
            "security": rec["security"], "additional_tools": rec["additional_tools"],
            "roles": rec["roles"], "roadmap": rec["roadmap"],
            "alternatives": rec["alternatives"], "decision_summary": rec["decision_summary"],
            "similar_projects": rec["similar_projects"]
        }
    }


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            team_size INTEGER NOT NULL DEFAULT 1,
            budget TEXT NOT NULL,
            expected_users TEXT NOT NULL DEFAULT '<1,000',
            security_level TEXT NOT NULL DEFAULT 'Medium',
            scalability_need TEXT NOT NULL DEFAULT 'Medium',
            team_experience TEXT NOT NULL DEFAULT 'Intermediate',
            deadline TEXT NOT NULL DEFAULT 'Standard',
            complexity TEXT NOT NULL,
            frontend TEXT NOT NULL,
            backend TEXT NOT NULL,
            database_name TEXT NOT NULL,
            hosting TEXT NOT NULL,
            architecture TEXT NOT NULL,
            scalability INTEGER NOT NULL DEFAULT 0,
            rule_fit_score INTEGER NOT NULL DEFAULT 0,
            development_time TEXT NOT NULL,
            estimated_cost TEXT NOT NULL,
            decision_summary TEXT NOT NULL DEFAULT '',
            factors_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        )
    """)

    existing = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(recommendations)").fetchall()
    }

    for column, definition in SCHEMA.items():
        if column not in existing:
            conn.execute(
                f"ALTER TABLE recommendations ADD COLUMN {column} {definition}"
            )

    conn.commit()
    conn.close()


# -----------------------------
# Rule base
# -----------------------------
PROJECTS = {
    "Portfolio": {
        "frontend": "HTML, CSS, JavaScript",
        "backend": "Flask",
        "database": "SQLite",
        "hosting": "GitHub Pages / Render",
        "alternatives": ["React.js", "Vue.js"],
        "reason": "Portfolio projects benefit from a lightweight frontend, simple content management and inexpensive deployment.",
        "security": ["HTTPS", "Input validation", "Spam protection", "Secure contact form"],
        "complexity_bias": 0
    },
    "Education": {
        "frontend": "React.js",
        "backend": "Python Flask",
        "database": "PostgreSQL",
        "hosting": "Render",
        "alternatives": ["Next.js", "Vue.js"],
        "reason": "Education systems often contain dashboards, courses, student records and dynamic content, so a component-based frontend and relational database are useful.",
        "security": ["Authentication", "Role-based access", "Password hashing", "HTTPS", "Input validation"],
        "complexity_bias": 2
    },
    "Hospital": {
        "frontend": "React.js",
        "backend": "Python Flask",
        "database": "PostgreSQL",
        "hosting": "AWS",
        "alternatives": ["Angular", "Django REST Framework"],
        "reason": "Hospital applications manage structured records and require controlled access, validation, backups and reliable APIs.",
        "security": ["Role-based access", "Strong authentication", "Encrypted communication", "Audit logs", "Database backups"],
        "complexity_bias": 4
    },
    "Banking": {
        "frontend": "React.js",
        "backend": "Python Flask",
        "database": "PostgreSQL",
        "hosting": "AWS",
        "alternatives": ["Angular", "Java Spring Boot"],
        "reason": "Banking applications require transactional data, strong authentication, auditing and infrastructure that can scale.",
        "security": ["Multi-factor authentication", "HTTPS", "Encryption", "Audit logging", "Input validation", "Database backups"],
        "complexity_bias": 4
    },
    "E-Commerce": {
        "frontend": "React.js",
        "backend": "Node.js / Flask",
        "database": "PostgreSQL",
        "hosting": "AWS / Render",
        "alternatives": ["Next.js", "Django"],
        "reason": "E-commerce applications need dynamic product views, user accounts, cart workflows and reliable transaction-related data.",
        "security": ["Authentication", "HTTPS", "Secure payment integration", "Rate limiting", "Input validation"],
        "complexity_bias": 3
    },
    "E-Sports": {
        "frontend": "React.js",
        "backend": "Node.js",
        "database": "MongoDB",
        "hosting": "AWS / Render",
        "alternatives": ["Next.js", "Express.js"],
        "reason": "E-sports applications can contain live scores, player profiles, leaderboards and frequently changing data.",
        "security": ["Authentication", "API security", "Rate limiting", "HTTPS", "Input validation"],
        "complexity_bias": 3
    }
}



# Curated real-world references by project domain. These are learning/reference
# links only; TechManager does not claim to analyze their private architecture.
SIMILAR_PROJECTS = {
    "E-Commerce": [
        {"name": "Amazon", "url": "https://www.amazon.com/", "tag": "Global marketplace", "why": "Reference for product discovery, cart, checkout and large-scale commerce flows."},
        {"name": "Flipkart", "url": "https://www.flipkart.com/", "tag": "Indian e-commerce", "why": "Reference for catalog, search, offers, payments and marketplace workflows."},
        {"name": "Meesho", "url": "https://www.meesho.com/", "tag": "Social commerce", "why": "Reference for marketplace-style product discovery and seller-oriented commerce."},
    ],
    "Education": [
        {"name": "EngiNotes", "url": "https://www.enginotes.in/", "tag": "Student platform", "why": "Reference for engineering notes, student content sharing and education-focused workflows."},
        {"name": "Coursera", "url": "https://www.coursera.org/", "tag": "Online learning", "why": "Reference for courses, learning content, learner accounts and progress-oriented experiences."},
        {"name": "Khan Academy", "url": "https://www.khanacademy.org/", "tag": "Learning platform", "why": "Reference for structured educational content and learner-focused experiences."},
    ],
    "Hospital": [
        {"name": "Practo", "url": "https://www.practo.com/", "tag": "Healthcare platform", "why": "Reference for doctor discovery, appointments, consultations and patient-facing workflows."},
        {"name": "Apollo Hospitals", "url": "https://www.apollohospitals.com/", "tag": "Hospital network", "why": "Reference for hospital services, appointments and digital healthcare journeys."},
        {"name": "Tata 1mg", "url": "https://www.1mg.com/", "tag": "Digital health", "why": "Reference for medicine, diagnostics and healthcare service workflows."},
    ],
    "Banking": [
        {"name": "HDFC Bank", "url": "https://www.hdfcbank.com/", "tag": "Digital banking", "why": "Reference for banking journeys, account services and secure customer interactions."},
        {"name": "ICICI Bank", "url": "https://www.icicibank.com/", "tag": "Digital banking", "why": "Reference for online banking services and customer self-service workflows."},
        {"name": "SBI", "url": "https://sbi.co.in/", "tag": "Banking", "why": "Reference for broad banking services and customer-facing digital workflows."},
    ],
    "E-Sports": [
        {"name": "ESPN", "url": "https://www.espn.com/", "tag": "Sports platform", "why": "Reference for scores, schedules, team/player information and sports content."},
        {"name": "Liquipedia", "url": "https://liquipedia.net/", "tag": "Esports wiki", "why": "Reference for tournaments, teams, players and structured esports data."},
        {"name": "FIFA", "url": "https://www.fifa.com/", "tag": "Sports ecosystem", "why": "Reference for competitions, teams, players and sports information experiences."},
    ],
    "Portfolio": [
        {"name": "GitHub Pages", "url": "https://pages.github.com/", "tag": "Static hosting", "why": "Reference for lightweight personal and project portfolio deployment."},
        {"name": "Vercel", "url": "https://vercel.com/", "tag": "Web platform", "why": "Reference for modern frontend and portfolio deployment workflows."},
        {"name": "Behance", "url": "https://www.behance.net/", "tag": "Creative portfolio", "why": "Reference for presenting projects, work samples and professional profiles."},
    ],
}

CHOICES = {
    "expected_users": {"<1,000": 0, "1,000–10,000": 1, "10,000–100,000": 2, "100,000+": 3},
    "security_level": {"Low": 0, "Medium": 1, "High": 2, "Critical": 3},
    "scalability_need": {"Low": 0, "Medium": 1, "High": 3},
    "team_experience": {"Beginner": 2, "Intermediate": 1, "Advanced": 0},
    "deadline": {"Short": 2, "Standard": 1, "Flexible": 0},
    "budget": {"Low": 0, "Medium": 1, "High": 2},
}


def generate_recommendation(project_type, team_size, budget,
                            expected_users="<1,000",
                            security_level="Medium",
                            scalability_need="Medium",
                            team_experience="Intermediate",
                            deadline="Standard"):
    """Deterministic, explainable recommendation engine.

    Scores are heuristics defined for this PBL prototype; they are not
    statistical probabilities or claims of a universally optimal stack.
    """
    p = PROJECTS.get(project_type, PROJECTS["Portfolio"])

    score = 1 + p["complexity_bias"]
    reasons = []

    if project_type in {"Hospital", "Banking"}:
        reasons.append(f"{project_type} has higher security and data-management requirements.")
    elif project_type in {"Education", "E-Commerce", "E-Sports"}:
        reasons.append(f"{project_type} typically requires dynamic application features.")

    if team_size <= 2:
        architecture = "Simple Monolithic Architecture"
        score += 1
        reasons.append("A small team favors a simpler monolithic architecture.")
    elif team_size <= 5:
        architecture = "Modular Monolithic Architecture"
        score += 2
        reasons.append("A medium-sized team can organize the system into clear modules without immediate microservice overhead.")
    else:
        architecture = "Scalable Microservices Architecture"
        score += 3
        reasons.append("A larger team can justify service boundaries and additional operational ownership.")

    if scalability_need == "High":
        score += 2
        reasons.append("High scalability demand increases the complexity and infrastructure requirements.")
    elif scalability_need == "Medium":
        score += 1

    if expected_users in {"10,000–100,000", "100,000+"}:
        score += 2
        reasons.append(f"The expected user volume ({expected_users}) increases scaling requirements.")
    elif expected_users == "1,000–10,000":
        score += 1

    if security_level in {"High", "Critical"}:
        score += 2
        reasons.append(f"{security_level} security requirements add authentication, validation and audit considerations.")
    elif security_level == "Medium":
        score += 1

    if budget == "Medium":
        score += 1
    elif budget == "High":
        score += 2
        reasons.append("A higher budget provides more room for managed infrastructure and development tooling.")

    if team_experience == "Beginner":
        score += 1
        reasons.append("Beginner teams benefit from keeping the architecture and tooling easier to operate.")

    if deadline == "Short":
        score += 1
        reasons.append("A short deadline favors a focused stack and avoids unnecessary infrastructure complexity.")

    complexity = "Beginner" if score <= 4 else "Intermediate" if score <= 8 else "Advanced"

    scalability = 45
    scalability += CHOICES["expected_users"].get(expected_users, 0) * 10
    scalability += CHOICES["scalability_need"].get(scalability_need, 0) * 8
    scalability += 10 if team_size > 5 else 6 if team_size > 2 else 0
    scalability += 10 if budget == "High" else 5 if budget == "Medium" else 0
    if project_type in {"Education", "Hospital", "Banking", "E-Commerce", "E-Sports"}:
        scalability += 10
    scalability = min(100, scalability)

    # A transparent heuristic fit score. This is deliberately labelled as a
    # rule-fit score rather than "accuracy" or "confidence".
    rule_fit_score = 60
    rule_fit_score += 8 if project_type in PROJECTS else 0
    rule_fit_score += 7 if team_size >= 1 else 0
    rule_fit_score += 7 if budget in CHOICES["budget"] else 0
    rule_fit_score += 6 if security_level in CHOICES["security_level"] else 0
    rule_fit_score += 6 if scalability_need in CHOICES["scalability_need"] else 0
    rule_fit_score += 3 if team_experience in CHOICES["team_experience"] else 0
    rule_fit_score += 3 if deadline in CHOICES["deadline"] else 0
    rule_fit_score = min(100, rule_fit_score)

    development_time = {
        "Beginner": "2 – 4 weeks",
        "Intermediate": "4 – 8 weeks",
        "Advanced": "8 – 16 weeks"
    }[complexity]

    # Planning ranges are prototype estimates, not market quotations.
    costs = {
        "Low": "₹1,000 – ₹5,000",
        "Medium": "₹6,000 – ₹15,000",
        "High": "₹16,000 – ₹50,000"
    }

    tools = {
        "Low": ["GitHub", "VS Code", "SQLite", "Render Free Tier"],
        "Medium": ["GitHub", "VS Code", "PostgreSQL", "Postman", "Render"],
        "High": ["GitHub Actions", "Docker", "Postman", "PostgreSQL", "AWS"]
    }[budget]

    if team_size == 1:
        roles = ["Full Stack Developer", "UI/UX Designer", "Tester"]
    elif team_size == 2:
        roles = ["Frontend Developer", "Backend Developer"]
    elif team_size <= 5:
        roles = ["Frontend Developer", "Backend Developer", "Database Developer", "UI/UX Designer", "QA / DevOps"]
    else:
        roles = ["Project Manager", "Frontend Developers", "Backend Developers", "Database Engineer", "UI/UX Designer", "QA Engineer", "DevOps Engineer"]

    security = list(p["security"])
    if security_level in {"High", "Critical"} and "Rate limiting" not in security:
        security.append("Rate limiting")
    if security_level == "Critical" and "Audit logging" not in security:
        security.append("Audit logging")

    if scalability_need == "High" or expected_users == "100,000+":
        hosting = "AWS"
        if p["database"] == "SQLite":
            database = "PostgreSQL"
        else:
            database = p["database"]
        reasons.append("High scale or user volume favors managed cloud infrastructure and a production-oriented database.")
    else:
        hosting = p["hosting"]
        database = p["database"]

    if team_experience == "Beginner":
        reasons.append("The recommendation keeps the core stack familiar and avoids unnecessary operational complexity.")

    if deadline == "Short":
        reasons.append("The roadmap prioritizes an MVP-first delivery approach.")

    roadmap = [
        ("Requirement Analysis", "Define users, objectives, scope and functional requirements."),
        ("Architecture & UI/UX", "Select the architecture and design the core user experience."),
        ("Database Design", "Define entities, relationships and data flow."),
        ("Core Development", "Build the frontend, backend and business rules."),
        ("Integration & Testing", "Connect modules and test important workflows."),
        ("Security Review", "Validate authentication, input handling and project-specific controls."),
        ("Deployment", "Deploy to the selected hosting platform and configure monitoring."),
        ("Maintenance", "Monitor, fix issues and improve the application.")
    ]

    factor_map = {
        "Project type": project_type,
        "Team size": str(team_size),
        "Budget": budget,
        "Expected users": expected_users,
        "Security": security_level,
        "Scalability need": scalability_need,
        "Team experience": team_experience,
        "Deadline": deadline
    }

    decision_summary = " ".join(dict.fromkeys(reasons))
    return {
        **p,
        "database": database,
        "hosting": hosting,
        "architecture": architecture,
        "complexity": complexity,
        "scalability": scalability,
        "rule_fit_score": rule_fit_score,
        "development_time": development_time,
        "estimated_cost": costs[budget],
        "additional_tools": tools,
        "similar_projects": SIMILAR_PROJECTS.get(project_type, []),
        "roles": roles,
        "roadmap": roadmap,
        "security": security,
        "decision_summary": decision_summary,
        "factors": factor_map
    }


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) AS n FROM recommendations").fetchone()["n"]
    avg_scale = conn.execute("SELECT COALESCE(ROUND(AVG(scalability)), 0) AS n FROM recommendations").fetchone()["n"]
    types = conn.execute("SELECT COUNT(DISTINCT project_type) AS n FROM recommendations").fetchone()["n"]
    recent = conn.execute("SELECT * FROM recommendations ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return render_template("index.html", total=total, avg_scale=avg_scale, types=types, recent=recent)


@app.route("/recommend", methods=["POST"])
def recommend():
    project_name = request.form.get("project_name", "").strip()
    project_type = request.form.get("project_type", "").strip()
    budget = request.form.get("budget", "").strip()
    expected_users = request.form.get("expected_users", "").strip()
    security_level = request.form.get("security_level", "").strip()
    scalability_need = request.form.get("scalability_need", "").strip()
    team_experience = request.form.get("team_experience", "").strip()
    deadline = request.form.get("deadline", "").strip()

    try:
        team_size = int(request.form.get("team_size", "1"))
    except (TypeError, ValueError):
        team_size = 0

    valid = (
        2 <= len(project_name) <= 100
        and project_type in PROJECTS
        and budget in CHOICES["budget"]
        and expected_users in CHOICES["expected_users"]
        and security_level in CHOICES["security_level"]
        and scalability_need in CHOICES["scalability_need"]
        and team_experience in CHOICES["team_experience"]
        and deadline in CHOICES["deadline"]
        and 1 <= team_size <= 100
    )
    if not valid:
        return redirect(url_for("home"))

    recommendation = generate_recommendation(
        project_type, team_size, budget, expected_users, security_level,
        scalability_need, team_experience, deadline
    )

    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO recommendations (
            project_name, project_type, team_size, budget, expected_users,
            security_level, scalability_need, team_experience, deadline,
            complexity, frontend, backend, database_name, hosting, architecture,
            scalability, rule_fit_score, development_time, estimated_cost,
            decision_summary, factors_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_name, project_type, team_size, budget, expected_users,
        security_level, scalability_need, team_experience, deadline,
        recommendation["complexity"], recommendation["frontend"],
        recommendation["backend"], recommendation["database"],
        recommendation["hosting"], recommendation["architecture"],
        recommendation["scalability"], recommendation["rule_fit_score"],
        recommendation["development_time"], recommendation["estimated_cost"],
        recommendation["decision_summary"], json.dumps(recommendation["factors"]),
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return redirect(url_for("details", record_id=record_id))


@app.route("/details/<int:record_id>")
def details(record_id):
    conn = get_db()
    record = conn.execute("SELECT * FROM recommendations WHERE id = ?", (record_id,)).fetchone()
    conn.close()

    if record is None:
        return redirect(url_for("history"))

    recommendation = generate_recommendation(
        record["project_type"], record["team_size"], record["budget"],
        record["expected_users"], record["security_level"],
        record["scalability_need"], record["team_experience"],
        record["deadline"]
    )
    return render_template("recommendation.html", record=record, **recommendation)


@app.route("/history")
def history():
    q = request.args.get("q", "").strip()
    project_type = request.args.get("type", "").strip()
    budget = request.args.get("budget", "").strip()

    sql = "SELECT * FROM recommendations WHERE 1=1"
    params = []
    if q:
        sql += " AND project_name LIKE ?"
        params.append(f"%{q}%")
    if project_type:
        sql += " AND project_type = ?"
        params.append(project_type)
    if budget:
        sql += " AND budget = ?"
        params.append(budget)
    sql += " ORDER BY id DESC"

    conn = get_db()
    records = conn.execute(sql, params).fetchall()
    total = conn.execute("SELECT COUNT(*) AS n FROM recommendations").fetchone()["n"]
    avg_scale = conn.execute("SELECT COALESCE(ROUND(AVG(scalability)), 0) AS n FROM recommendations").fetchone()["n"]
    advanced = conn.execute("SELECT COUNT(*) AS n FROM recommendations WHERE complexity='Advanced'").fetchone()["n"]
    distinct_projects = conn.execute("SELECT COUNT(DISTINCT project_type) AS n FROM recommendations").fetchone()["n"]
    conn.close()

    return render_template(
        "history.html", records=records, total=total, avg_scale=avg_scale,
        advanced=advanced, distinct_projects=distinct_projects, q=q,
        selected_type=project_type, selected_budget=budget
    )


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = get_db()
    conn.execute("DELETE FROM recommendations WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("history"))


@app.route("/export/<int:record_id>.json")
def export_json(record_id):
    conn = get_db()
    record = conn.execute("SELECT * FROM recommendations WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    if record is None:
        return jsonify({"error": "Recommendation not found"}), 404
    response = jsonify(serialize_record(record))
    response.headers["Content-Disposition"] = f'attachment; filename="techmanager-{record_id}.json"'
    return response


@app.route("/compare")
def compare():
    raw_values = request.args.getlist("ids")
    ids = []
    for raw_ids in raw_values:
        for value in raw_ids.split(","):
            try:
                number = int(value)
                if number > 0 and number not in ids:
                    ids.append(number)
            except ValueError:
                pass
    ids = ids[:3]
    if len(ids) < 2:
        return redirect(url_for("history"))
    placeholders = ",".join("?" for _ in ids)
    conn = get_db()
    rows = conn.execute(f"SELECT * FROM recommendations WHERE id IN ({placeholders}) ORDER BY id DESC", ids).fetchall()
    conn.close()
    records = [dict(r) for r in rows]
    if len(records) < 2:
        return redirect(url_for("history"))
    return render_template("compare.html", records=records, recommendations=[row_to_recommendation(r) for r in rows])


@app.route("/api")
def api_docs():
    return jsonify({
        "service": "TechManager API",
        "version": APP_VERSION,
        "endpoint": "POST /api/recommend",
        "required": ["project_type", "team_size", "budget"],
        "optional": ["expected_users", "security_level", "scalability_need", "team_experience", "deadline"],
        "note": "Scores are deterministic heuristic planning indicators, not statistical accuracy or guarantees."
    })


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json(silent=True) or {}
    required = ["project_type", "team_size", "budget"]
    if any(key not in data for key in required):
        return jsonify({"error": "project_type, team_size and budget are required"}), 400

    try:
        team_size = int(data["team_size"])
    except (TypeError, ValueError):
        return jsonify({"error": "team_size must be an integer"}), 400

    try:
        recommendation = generate_recommendation(
            data["project_type"], team_size, data["budget"],
            data.get("expected_users", "<1,000"),
            data.get("security_level", "Medium"),
            data.get("scalability_need", "Medium"),
            data.get("team_experience", "Intermediate"),
            data.get("deadline", "Standard")
        )
    except KeyError:
        return jsonify({"error": "Invalid recommendation input"}), 400

    return jsonify({
        "project_type": data["project_type"],
        "team_size": team_size,
        "budget": data["budget"],
        "recommendation": recommendation
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "TechManager", "database": str(DATABASE.name)})


# Initialize both local and WSGI deployments.
init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
