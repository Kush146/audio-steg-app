import sqlite3
import hashlib
import random
import secrets

DB_NAME = "users.db"

def create_users_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        pin TEXT,
        secret_key TEXT
    )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    pin = str(random.randint(1000, 9999))
    key = secrets.token_hex(4)
    try:
        cursor.execute("INSERT INTO users (email, password, pin, secret_key) VALUES (?, ?, ?, ?)",
                       (email, hash_password(password), pin, key))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_user_credentials(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT pin, secret_key FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result
