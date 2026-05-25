import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bank.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS accounts")
    cursor.execute("DROP TABLE IF EXISTS secret_projects")
    cursor.execute("DROP TABLE IF EXISTS attack_log")

    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

    cursor.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            account_number TEXT,
            balance REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE secret_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            budget REAL,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE attack_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now','localtime')),
            input_used TEXT,
            attack_type TEXT,
            success INTEGER,
            mode TEXT
        )
    """)

    cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [
        ("admin",    "SuperSecret@123", "admin"),
        ("john_doe", "john2024",        "user"),
        ("alice",    "alice@pass",      "user"),
        ("bob",      "bob#secure",      "user"),
    ])

    cursor.executemany("INSERT INTO accounts (user_id, account_number, balance) VALUES (?, ?, ?)", [
        (1, "ACC-0001", 9999999.00),
        (2, "ACC-1042", 24500.75),
        (3, "ACC-2087", 87320.50),
        (4, "ACC-3301", 15000.00),
    ])

    cursor.executemany("INSERT INTO secret_projects (project_name, budget, status) VALUES (?, ?, ?)", [
        ("Operation Goldfish",  5000000, "CLASSIFIED"),
        ("Project Nighthawk",   8200000, "TOP SECRET"),
        ("Alpha Vault",        12000000, "CONFIDENTIAL"),
    ])

    conn.commit()
    conn.close()
    print(f"[OK] Database initialized at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
