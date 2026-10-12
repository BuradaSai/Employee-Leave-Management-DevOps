
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.secret_key = "employee-leave-demo-key"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "leave.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee TEXT NOT NULL,
                leave_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)


def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))

            if role and session.get("role") != role:
                flash("You are not authorized to access that page.")
                return redirect(url_for("dashboard"))

            return view(*args, **kwargs)
        return wrapped
    return decorator


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        
        

        accounts = {
            "employee1": {"password": "emp1123", "role": "employee"},
            "employee2": {"password": "emp2123", "role": "employee"},
            "employee3": {"password": "emp3123", "role": "employee"},
            "manager": {"password": "mgr123", "role": "manager"},
        }


        account = accounts.get(username)

        if account and account["password"] == password:
            session["user"] = username
            session["role"] = account["role"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")



@app.route("/dashboard")
@login_required()
def dashboard():
    from datetime import date

    with get_db() as db:
        if session["role"] == "employee":
            leaves = db.execute(
                "SELECT * FROM leaves WHERE employee = ? ORDER BY id DESC",
                (session["user"],)
            ).fetchall()
        else:
            leaves = db.execute(
                "SELECT * FROM leaves ORDER BY id DESC"
            ).fetchall()

    return render_template(
        "dashboard.html",
        leaves=leaves,
        role=session["role"],
        user=session["user"],
        today=date.today().isoformat()
    )



@app.route("/apply", methods=["POST"])
@login_required("employee")
def apply_leave():
    leave_type = request.form.get("leave_type", "")
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    reason = request.form.get("reason", "").strip()

    from datetime import date

    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        flash("Please enter valid leave dates.")
        return redirect(url_for("dashboard"))

    if leave_type not in {"Casual", "Sick", "Earned"}:
        flash("Select a valid leave type.")
    elif start < date.today():
        flash("Leave cannot start in the past.")
    elif end < start:
        flash("End date cannot be before start date.")
    elif not reason:
        flash("Please provide a reason.")
    else:
        with get_db() as db:
            db.execute("""
                INSERT INTO leaves
                (employee, leave_type, start_date, end_date, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session["user"], leave_type, start_date, end_date, reason
            ))

        flash("Leave request submitted successfully.")

    return redirect(url_for("dashboard"))


@app.route("/leave/<int:leave_id>/<action>", methods=["POST"])
@login_required("manager")
def update_leave(leave_id, action):
    if action not in {"approve", "reject"}:
        flash("Invalid action.")
        return redirect(url_for("dashboard"))

    new_status = "Approved" if action == "approve" else "Rejected"

    with get_db() as db:
        cursor = db.execute("""
            UPDATE leaves
            SET status = ?
            WHERE id = ? AND status = 'Pending'
        """, (new_status, leave_id))

    if cursor.rowcount:
        flash(f"Leave request {new_status.lower()} successfully.")
    else:
        flash("Request not found or already processed.")

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
