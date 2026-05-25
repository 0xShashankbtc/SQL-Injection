import streamlit as st
import sqlite3
import os
import time
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/bank.db")

st.set_page_config(
    page_title="SQLi Demo — Hacker Console",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Space Mono', monospace; }

  .stApp { background: #0a0d14; }

  section[data-testid="stSidebar"] {
    background: #0d1019 !important;
    border-right: 1px solid #1e2535;
  }

  .big-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: #e8eaf0;
    margin-bottom: 4px;
  }

  .sub { font-size: 12px; color: #5a6277; margin-bottom: 24px; }

  .metric-card {
    background: #111620;
    border: 1px solid #1e2535;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
  }

  .metric-label { font-size: 10px; color: #5a6277; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px; }
  .metric-value { font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 800; }

  .red-card   { border-color: rgba(255,59,92,0.4)  !important; }
  .green-card { border-color: rgba(0,229,160,0.4)  !important; }
  .red-val    { color: #ff3b5c; }
  .green-val  { color: #00e5a0; }

  .payload-box {
    background: #070a0f;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 14px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #e8b86d;
    word-break: break-all;
    line-height: 1.6;
    margin: 8px 0;
  }

  .attack-row-success { background: rgba(255,59,92,0.08); border-left: 3px solid #ff3b5c; padding: 6px 12px; border-radius: 4px; margin:3px 0; font-size:12px; }
  .attack-row-blocked  { background: rgba(0,229,160,0.06); border-left: 3px solid #00e5a0; padding: 6px 12px; border-radius: 4px; margin:3px 0; font-size:12px; }
</style>
""", unsafe_allow_html=True)

def get_db():
    if not os.path.exists(DB_PATH):
        st.error("Database not found. Run `python database/init_db.py` first.")
        st.stop()
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def load_table(table):
    conn = get_db()
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def load_attack_log():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM attack_log ORDER BY id DESC LIMIT 20", conn)
    conn.close()
    return df

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="big-title">🔐 SQLi<br/>Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Live Demo Dashboard</div>', unsafe_allow_html=True)
    st.divider()

    page = st.radio("Navigation", [
        "📊 Live DB Viewer",
        "💥 Attack Simulator",
        "🛡 Defence Explained",
        "📋 Code Diff",
    ])

    st.divider()
    if st.button("🔄 Reset Database", use_container_width=True):
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../database"))
        from init_db import init_db
        init_db()
        st.success("Database reset!")
        time.sleep(1)
        st.rerun()

    st.caption("Flask app → http://localhost:5000")

# ═══════════════════════════════════════════════════════════════════
#  PAGE 1 — LIVE DB VIEWER
# ═══════════════════════════════════════════════════════════════════
if page == "📊 Live DB Viewer":
    st.markdown('<div class="big-title">📊 Live Database Viewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">This is the actual data stored in bank.db — what an attacker wants to steal</div>', unsafe_allow_html=True)

    # Auto-refresh
    auto = st.toggle("Auto-refresh every 3s", value=False)

    tab1, tab2, tab3, tab4 = st.tabs(["👤 Users", "💰 Accounts", "🔒 Secret Projects", "⚔ Attack Log"])

    with tab1:
        st.markdown("### users table")
        st.markdown("> ⚠ Passwords stored in **plaintext** for demo purposes")
        df = load_table("users")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### accounts table")
        df = load_table("accounts")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### secret_projects table 🔥")
        st.error("This table is NEVER shown in the UI — attackers find it via UNION injection")
        df = load_table("secret_projects")
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### attack_log table — live feed")
        df = load_attack_log()
        if df.empty:
            st.info("No attacks logged yet. Try the login form at localhost:5000")
        else:
            for _, row in df.iterrows():
                icon = "🔴" if row["success"] else "🟢"
                mode_tag = "VULN" if row["mode"] == "vulnerable" else "SECURE"
                result = "BYPASSED" if row["success"] else "BLOCKED"
                st.markdown(
                    f'<div class="{"attack-row-success" if row["success"] else "attack-row-blocked"}">'
                    f'{icon} <b>{row["timestamp"]}</b> | [{mode_tag}] | {row["attack_type"]} | {result}<br/>'
                    f'<span style="color:#5a6277;font-size:11px;">Input: {row["input_used"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    if auto:
        time.sleep(3)
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
#  PAGE 2 — ATTACK SIMULATOR
# ═══════════════════════════════════════════════════════════════════
elif page == "💥 Attack Simulator":
    st.markdown('<div class="big-title">💥 Attack Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Run SQL injection attacks directly — see the raw query and result</div>', unsafe_allow_html=True)

    mode = st.selectbox("Mode", ["vulnerable", "secure"], format_func=lambda x: f"⚠ Vulnerable" if x == "vulnerable" else "🛡 Secure")

    preset = st.selectbox("Quick Payloads", [
        "Custom",
        "' OR '1'='1  →  Password bypass",
        "' OR 1=1 --  →  Username bypass",
        "admin' --    →  Skip password check",
        "' UNION SELECT 1,2,3,4 --  →  UNION probe",
    ])

    col1, col2 = st.columns(2)
    with col1:
        if preset != "Custom":
            default_user = preset.split("→")[0].strip().split()[0] if "username" in preset.lower() else "admin"
            default_pass = preset.split("→")[0].strip() if "password" in preset.lower() or "'" in preset else "test"
        else:
            default_user, default_pass = "admin", "wrongpass"

        username = st.text_input("Username", value=default_user)
    with col2:
        password = st.text_input("Password", value=default_pass if preset == "Custom" else preset.split("→")[0].strip().split()[0])

    if st.button("🚀 Execute Attack", use_container_width=True):
        if mode == "vulnerable":
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            st.markdown("**Query executed:**")
            st.markdown(f'<div class="payload-box">{query}</div>', unsafe_allow_html=True)
            try:
                conn = get_db()
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                conn.close()
                if rows:
                    st.error(f"🔴 ATTACK SUCCEEDED — {len(rows)} row(s) returned!")
                    st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
                else:
                    st.success("🟢 No rows returned (attack failed)")
            except Exception as e:
                st.warning(f"⚠ SQL Error (also dangerous — leaks DB info):\n`{e}`")
        else:
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            st.markdown("**Parameterized query (values handled separately):**")
            st.markdown(f'<div class="payload-box">Query:  {query}\nValues: ({repr(username)}, {repr(password)})</div>', unsafe_allow_html=True)
            try:
                conn = get_db()
                cursor = conn.execute(query, (username, password))
                rows = cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                conn.close()
                if rows:
                    st.success(f"✅ Legitimate login — user found")
                    st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True)
                else:
                    st.success("🛡 ATTACK BLOCKED — No rows returned. Injection treated as literal string.")
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════
#  PAGE 3 — DEFENCE EXPLAINED
# ═══════════════════════════════════════════════════════════════════
elif page == "🛡 Defence Explained":
    st.markdown('<div class="big-title">🛡 Defence Mechanisms</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">5 layers of protection against SQL injection</div>', unsafe_allow_html=True)

    defences = [
        ("1️⃣ Parameterized Queries", "#00e5a0",
         "The #1 fix. Values are sent to the DB separately from the query structure. The DB driver escapes them automatically.",
         "cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))"),
        ("2️⃣ Input Validation", "#00b4d8",
         "Reject inputs that contain SQL special characters like ', --, ;, UNION before they ever reach the DB.",
         "import re\nif re.search(r\"[';\\-\\-]\", username):\n    return 'Invalid input'"),
        ("3️⃣ Hide Error Messages", "#f4a261",
         "Never expose raw SQL errors to the user. Log them server-side only. Error messages reveal DB structure.",
         "try:\n    ...\nexcept Exception as e:\n    log(e)  # server only\n    return 'Something went wrong'"),
        ("4️⃣ Least Privilege DB User", "#e76f51",
         "The app's DB user should only have SELECT permission on the tables it needs. It should NOT have DROP, INSERT on sensitive tables.",
         "GRANT SELECT ON users TO 'app_user'@'localhost';\nREVOKE DROP, CREATE ON *.* FROM 'app_user';"),
        ("5️⃣ Web Application Firewall", "#9d4edd",
         "A WAF (e.g. ModSecurity, AWS WAF) detects and blocks known SQL injection patterns at the network layer before hitting your app.",
         "# Example WAF rule (ModSecurity)\nSecRule ARGS \"@detectSQLi\" \"id:1001,deny,status:403\""),
    ]

    for title, color, desc, code in defences:
        with st.expander(title, expanded=(title.startswith("1"))):
            st.markdown(f"<span style='color:{color}'>{desc}</span>", unsafe_allow_html=True)
            st.code(code, language="python")

# ═══════════════════════════════════════════════════════════════════
#  PAGE 4 — CODE DIFF
# ═══════════════════════════════════════════════════════════════════
elif page == "📋 Code Diff":
    st.markdown('<div class="big-title">📋 Side-by-Side Code Diff</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Exactly what changes between vulnerable and secure code</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ❌ Vulnerable")
        st.code("""
# VULNERABLE — String interpolation
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # !! BAD: raw f-string query !!
    query = f\"\"\"
      SELECT * FROM users
      WHERE username = '{username}'
      AND password  = '{password}'
    \"\"\"

    conn = get_db()
    user = conn.execute(query).fetchone()

    if user:
        session['user'] = dict(user)
        return redirect('/dashboard')
    return render_template('login.html',
        error='Invalid credentials')
        """, language="python")

    with col2:
        st.markdown("### ✅ Secure")
        st.code("""
# SECURE — Parameterized query
@app.route('/secure-login', methods=['POST'])
def secure_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # GOOD: placeholders + tuple of values
    query = \"\"\"
      SELECT * FROM users
      WHERE username = ?
      AND password  = ?
    \"\"\"

    conn = get_db()
    user = conn.execute(
        query,
        (username, password)   # <-- values here
    ).fetchone()

    if user:
        session['user'] = dict(user)
        return redirect('/dashboard')
    return render_template('login.html',
        error='Invalid credentials')
        """, language="python")

    st.divider()
    st.markdown("### 🔍 What changes?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Lines Changed", "3", delta=None)
        st.caption("Minimal code change, maximum security gain")
    with c2:
        st.metric("f-string removed", "YES", delta=None)
        st.caption("No more direct variable embedding")
    with c3:
        st.metric("Values escaped by", "DB Driver", delta=None)
        st.caption("Automatic, reliable, impossible to bypass")
