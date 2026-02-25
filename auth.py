import sqlite3
import hashlib

def connect_db():
    return sqlite3.connect("users.db")

def create_users_table():
    conn = connect_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT)
    """)

    conn.commit()
    conn.close()

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def signup_user(u, e, p):
    conn = connect_db()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users VALUES (?,?,?)", (u, e, hash_password(p)))
        conn.commit()
        return "success"
    except:
        return "exists"

def login_user(u, p):
    conn = connect_db()
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE username=?", (u,))
    data = c.fetchone()

    conn.close()

    if data and data[0] == hash_password(p):
        return "success"

    return "fail"
