from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "demo-secret-key-123"

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/bank.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_attack(input_used, attack_type, success, mode):
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO attack_log (input_used, attack_type, success, mode) VALUES (?, ?, ?, ?)",
            (input_used, attack_type, int(success), mode)
        )
        conn.commit()
        conn.close()
    except:
        pass

# ─── HOME ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("login"))

# ─── VULNERABLE LOGIN ─────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    sql_query = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # !! VULNERABLE: raw string interpolation !!
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        sql_query = query

        try:
            conn = get_db()
            cursor = conn.execute(query)
            user = cursor.fetchone()
            conn.close()

            if user:
                session["user"] = dict(user)
                session["mode"] = "vulnerable"
                log_attack(f"user={username} pass={password}", "Login Bypass", True, "vulnerable")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid credentials."
                log_attack(f"user={username} pass={password}", "Login Attempt", False, "vulnerable")
        except Exception as e:
            error = f"Database Error: {str(e)}"
            sql_query = query
            log_attack(f"user={username} pass={password}", "SQLi Error", False, "vulnerable")

    return render_template("login.html", error=error, sql_query=sql_query, mode="vulnerable")

# ─── SECURE LOGIN ─────────────────────────────────────────────────────────────
@app.route("/secure-login", methods=["GET", "POST"])
def secure_login():
    error = None
    sql_query = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # SECURE: parameterized query
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        sql_query = f"SELECT * FROM users WHERE username = ? AND password = ?  →  Values: ('{username}', '{password}')"

        try:
            conn = get_db()
            cursor = conn.execute(query, (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session["user"] = dict(user)
                session["mode"] = "secure"
                log_attack(f"user={username} pass={password}", "Login Attempt", True, "secure")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid credentials."
                log_attack(f"user={username} pass={password}", "Blocked Attack", False, "secure")
        except Exception as e:
            error = "Something went wrong. Please try again."
            log_attack(f"user={username} pass={password}", "Error", False, "secure")

    return render_template("login.html", error=error, sql_query=sql_query, mode="secure")

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    user = session["user"]
    mode = session.get("mode", "vulnerable")

    conn = get_db()
    account = conn.execute("SELECT * FROM accounts WHERE user_id = ?", (user["id"],)).fetchone()
    conn.close()

    return render_template("dashboard.html", user=user, account=account, mode=mode)

# ─── LOGOUT ───────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─── RESET DB (for demo resets) ──────────────────────────────────────────────
@app.route("/reset-db")
def reset_db():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../database"))
    from init_db import init_db
    init_db()
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
