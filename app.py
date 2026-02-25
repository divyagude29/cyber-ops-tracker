from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "change-this-to-any-random-string"
DB = "tracker.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        severity TEXT NOT NULL,
        owner TEXT NOT NULL,
        due_date TEXT,
        status TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT,
        assignee TEXT NOT NULL,
        due_date TEXT,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        incident_date TEXT NOT NULL,
        severity TEXT NOT NULL,
        system TEXT,
        status TEXT NOT NULL,
        summary TEXT,
        created_at TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        owner TEXT NOT NULL,
        version TEXT NOT NULL,
        last_updated TEXT NOT NULL,
        next_review TEXT,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


@app.route("/")
@app.route("/dashboard")
def dashboard():
    conn = db()
    risks = conn.execute("SELECT * FROM risks ORDER BY created_at DESC").fetchall()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    incidents = conn.execute("SELECT * FROM incidents ORDER BY created_at DESC").fetchall()
    documents = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()

    today = date.today()

    open_risks = sum(1 for r in risks if r["status"] != "Closed")
    high_risks = sum(1 for r in risks if r["severity"] in ("High", "Critical") and r["status"] != "Closed")

    overdue_tasks = 0
    for t in tasks:
        due = parse_date(t["due_date"])
        if due and due < today and t["status"] != "Closed":
            overdue_tasks += 1

    open_incidents = sum(1 for i in incidents if i["status"] != "Closed")

    review_soon = 0
    for d in documents:
        nxt = parse_date(d["next_review"])
        if nxt and 0 <= (nxt - today).days <= 30:
            review_soon += 1

    return render_template(
        "dashboard.html",
        open_risks=open_risks,
        high_risks=high_risks,
        overdue_tasks=overdue_tasks,
        open_incidents=open_incidents,
        review_soon=review_soon,
        risks=risks[:5],
        tasks=tasks[:5],
        incidents=incidents[:5],
        documents=documents[:5],
    )


@app.route("/risks")
def risks():
    conn = db()
    rows = conn.execute("SELECT * FROM risks ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("risks.html", risks=rows)


@app.route("/risks/add", methods=["POST"])
def add_risk():
    title = request.form.get("title", "").strip()
    severity = request.form.get("severity", "Low")
    owner = request.form.get("owner", "").strip()
    due_date = request.form.get("due_date", "")
    status = request.form.get("status", "Open")
    notes = request.form.get("notes", "").strip()

    if not title or not owner:
        flash("Risk title and owner are required.", "danger")
        return redirect(url_for("risks"))

    conn = db()
    conn.execute("""
        INSERT INTO risks (title, severity, owner, due_date, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, severity, owner, due_date, status, notes, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    flash("Risk added.", "success")
    return redirect(url_for("risks"))


@app.route("/risks/delete/<int:item_id>", methods=["POST"])
def delete_risk(item_id):
    conn = db()
    conn.execute("DELETE FROM risks WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Risk deleted.", "warning")
    return redirect(url_for("risks"))


@app.route("/tasks")
def tasks():
    conn = db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("tasks.html", tasks=rows)


@app.route("/tasks/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()
    assignee = request.form.get("assignee", "").strip()
    due_date = request.form.get("due_date", "")
    priority = request.form.get("priority", "Low")
    status = request.form.get("status", "Open")
    notes = request.form.get("notes", "").strip()

    if not title or not assignee:
        flash("Task title and assignee are required.", "danger")
        return redirect(url_for("tasks"))

    conn = db()
    conn.execute("""
        INSERT INTO tasks (title, category, assignee, due_date, priority, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, category, assignee, due_date, priority, status, notes, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    flash("Task added.", "success")
    return redirect(url_for("tasks"))


@app.route("/tasks/delete/<int:item_id>", methods=["POST"])
def delete_task(item_id):
    conn = db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Task deleted.", "warning")
    return redirect(url_for("tasks"))


@app.route("/incidents")
def incidents():
    conn = db()
    rows = conn.execute("SELECT * FROM incidents ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("incidents.html", incidents=rows)


@app.route("/incidents/add", methods=["POST"])
def add_incident():
    title = request.form.get("title", "").strip()
    incident_date = request.form.get("incident_date", "")
    severity = request.form.get("severity", "Low")
    system = request.form.get("system", "").strip()
    status = request.form.get("status", "Open")
    summary = request.form.get("summary", "").strip()

    if not title or not incident_date:
        flash("Incident title and date are required.", "danger")
        return redirect(url_for("incidents"))

    conn = db()
    conn.execute("""
        INSERT INTO incidents (title, incident_date, severity, system, status, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, incident_date, severity, system, status, summary, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    flash("Incident added.", "success")
    return redirect(url_for("incidents"))


@app.route("/incidents/delete/<int:item_id>", methods=["POST"])
def delete_incident(item_id):
    conn = db()
    conn.execute("DELETE FROM incidents WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Incident deleted.", "warning")
    return redirect(url_for("incidents"))


@app.route("/documents")
def documents():
    conn = db()
    rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("documents.html", documents=rows)


@app.route("/documents/add", methods=["POST"])
def add_document():
    name = request.form.get("name", "").strip()
    doc_type = request.form.get("doc_type", "Procedure")
    owner = request.form.get("owner", "").strip()
    version = request.form.get("version", "").strip()
    last_updated = request.form.get("last_updated", "")
    next_review = request.form.get("next_review", "")

    if not name or not owner or not version or not last_updated:
        flash("Name, owner, version, and last updated are required.", "danger")
        return redirect(url_for("documents"))

    conn = db()
    conn.execute("""
        INSERT INTO documents (name, doc_type, owner, version, last_updated, next_review, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, doc_type, owner, version, last_updated, next_review, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    flash("Document added.", "success")
    return redirect(url_for("documents"))


@app.route("/documents/delete/<int:item_id>", methods=["POST"])
def delete_document(item_id):
    conn = db()
    conn.execute("DELETE FROM documents WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Document deleted.", "warning")
    return redirect(url_for("documents"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)