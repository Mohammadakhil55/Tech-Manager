from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"


# -----------------------------
# Database helpers
# -----------------------------
SCHEMA = {
    "project_name": "TEXT NOT NULL",
    "project_type": "TEXT NOT NULL",
    "team_size": "INTEGER NOT NULL DEFAULT 1",
    "budget": "TEXT NOT NULL",
    "complexity": "TEXT NOT NULL",
    "frontend": "TEXT NOT NULL",
    "backend": "TEXT NOT NULL",
    "database_name": "TEXT NOT NULL",
    "hosting": "TEXT NOT NULL",
    "architecture": "TEXT NOT NULL",
    "scalability": "INTEGER NOT NULL DEFAULT 0",
    "development_time": "TEXT NOT NULL",
    "estimated_cost": "TEXT NOT NULL",
    "created_at": "TEXT NOT NULL"
}


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            team_size INTEGER NOT NULL DEFAULT 1,
            budget TEXT NOT NULL,
            complexity TEXT NOT NULL,
            frontend TEXT NOT NULL,
            backend TEXT NOT NULL,
            database_name TEXT NOT NULL,
            hosting TEXT NOT NULL,
            architecture TEXT NOT NULL,
            scalability INTEGER NOT NULL DEFAULT 0,
            development_time TEXT NOT NULL,
            estimated_cost TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Safe migration for older versions of this project.
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
# Recommendation engine
# -----------------------------
PROJECTS = {
    "Portfolio": {
        "frontend": "HTML, CSS, JavaScript",
        "backend": "Flask",
        "database": "SQLite",
        "hosting": "GitHub Pages / Render",
        "alternatives": "React.js, Vue.js",
        "reason": "Portfolio projects benefit from a lightweight frontend, simple content management and inexpensive deployment.",
        "security": ["HTTPS", "Input validation", "Spam protection", "Secure contact form"]
    },
    "Education": {
        "frontend": "React.js",
        "backend": "Python Flask",
        "database": "PostgreSQL",
        "hosting": "Render",
        "alternatives": "Next.js, Vue.js",
        "reason": "Education systems often contain dashboards, courses, student records and dynamic content, so a component-based frontend and relational database are useful.",
        "security": ["Authentication", "Role-based access", "Password hashing", "HTTPS", "Input validation"]
    },
    "Hospital": {
        "frontend": "React.js",
        "backend": "Python Flask",
        "database": "PostgreSQL",
        "hosting": "AWS",
        "alternatives": "Angular, Django REST Framework",
        "reason": "Hospital applications manage structured records and require controlled access, validation, backups and reliable APIs.",
        "security": ["Role-based access", "Strong authentication", "Encrypted communication", "Audit logs", "Database backups"]
    },
    "Banking": {
        "frontend": "React.js",
        "backend": "Python Flask",
        "database": "PostgreSQL",
        "hosting": "AWS",
        "alternatives": "Angular, Java Spring Boot",
        "reason": "Banking applications require transactional data, strong authentication, auditing and infrastructure that can scale.",
        "security": ["Multi-factor authentication", "HTTPS", "Encryption", "Audit logging", "Input validation", "Database backups"]
    },
    "E-Commerce": {
        "frontend": "React.js",
        "backend": "Node.js / Flask",
        "database": "PostgreSQL",
        "hosting": "AWS / Render",
        "alternatives": "Next.js, Django",
        "reason": "E-commerce applications need dynamic product views, user accounts, cart workflows and reliable transaction-related data.",
        "security": ["Authentication", "HTTPS", "Secure payment integration", "Rate limiting", "Input validation"]
    },
    "E-Sports": {
        "frontend": "React.js",
        "backend": "Node.js",
        "database": "MongoDB",
        "hosting": "AWS / Render",
        "alternatives": "Next.js, Express.js",
        "reason": "E-sports applications can contain live scores, player profiles, leaderboards and frequently changing data.",
        "security": ["Authentication", "API security", "Rate limiting", "HTTPS", "Input validation"]
    }
}


def generate_recommendation(project_type, team_size, budget):
    p = PROJECTS.get(project_type, PROJECTS["Portfolio"])

    score = 1

    if project_type in {"Hospital", "Banking"}:
        score += 4
    elif project_type in {"Education", "E-Commerce", "E-Sports"}:
        score += 3

    if team_size <= 2:
        score += 1
    elif team_size <= 5:
        score += 2
    else:
        score += 3

    if budget == "Medium":
        score += 1
    elif budget == "High":
        score += 2

    complexity = "Beginner" if score <= 3 else "Intermediate" if score <= 6 else "Advanced"

    if team_size <= 2:
        architecture = "Simple Monolithic Architecture"
    elif team_size <= 5:
        architecture = "Modular Monolithic Architecture"
    else:
        architecture = "Scalable Microservices Architecture"

    scalability = 50
    if project_type in {"Education", "Hospital", "Banking", "E-Commerce", "E-Sports"}:
        scalability += 20
    if team_size > 5:
        scalability += 15
    elif team_size > 2:
        scalability += 10
    if budget == "High":
        scalability += 15
    elif budget == "Medium":
        scalability += 8
    scalability = min(100, scalability)

    development_time = {
        "Beginner": "2 – 4 weeks",
        "Intermediate": "4 – 8 weeks",
        "Advanced": "8 – 16 weeks"
    }[complexity]

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

    roadmap = [
        ("Requirement Analysis", "Define users, objectives, scope and functional requirements."),
        ("UI/UX Design", "Design screens, navigation and the user experience."),
        ("Database Design", "Define entities, relationships and data flow."),
        ("Frontend Development", "Build responsive client-side interfaces."),
        ("Backend Development", "Implement APIs, business logic and validation."),
        ("Integration & Testing", "Connect modules and test important workflows."),
        ("Deployment", "Deploy the application to the selected hosting platform."),
        ("Maintenance", "Monitor, fix issues and improve the application.")
    ]

    return {
        **p,
        "database": p["database"],
        "architecture": architecture,
        "complexity": complexity,
        "scalability": scalability,
        "development_time": development_time,
        "estimated_cost": costs[budget],
        "additional_tools": tools,
        "roles": roles,
        "roadmap": roadmap
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
    recent = conn.execute(
        "SELECT * FROM recommendations ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()

    return render_template(
        "index.html",
        total=total,
        avg_scale=avg_scale,
        types=types,
        recent=recent
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    project_name = request.form.get("project_name", "").strip()
    project_type = request.form.get("project_type", "").strip()
    budget = request.form.get("budget", "").strip()

    try:
        team_size = int(request.form.get("team_size", "1"))
    except (TypeError, ValueError):
        team_size = 1

    if not project_name or project_type not in PROJECTS or budget not in {"Low", "Medium", "High"}:
        return redirect(url_for("home"))

    team_size = max(1, min(team_size, 100))
    recommendation = generate_recommendation(project_type, team_size, budget)

    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO recommendations (
            project_name, project_type, team_size, budget, complexity,
            frontend, backend, database_name, hosting, architecture,
            scalability, development_time, estimated_cost, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_name, project_type, team_size, budget,
        recommendation["complexity"], recommendation["frontend"],
        recommendation["backend"], recommendation["database"],
        recommendation["hosting"], recommendation["architecture"],
        recommendation["scalability"], recommendation["development_time"],
        recommendation["estimated_cost"],
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return redirect(url_for("details", record_id=record_id))


@app.route("/details/<int:record_id>")
def details(record_id):
    conn = get_db()
    record = conn.execute(
        "SELECT * FROM recommendations WHERE id = ?", (record_id,)
    ).fetchone()
    conn.close()

    if record is None:
        return redirect(url_for("history"))

    recommendation = generate_recommendation(
        record["project_type"], record["team_size"], record["budget"]
    )

    return render_template(
        "recommendation.html",
        record=record,
        **recommendation
    )


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
        "history.html",
        records=records,
        total=total,
        avg_scale=avg_scale,
        advanced=advanced,
        distinct_projects=distinct_projects,
        q=q,
        selected_type=project_type,
        selected_budget=budget
    )


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    conn = get_db()
    conn.execute("DELETE FROM recommendations WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("history"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "TechManager"})


init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
