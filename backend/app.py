from flask import Flask, request, jsonify
import sqlite3
import os
import logging

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "database.db")
APP_PORT = int(os.getenv("APP_PORT", 5000))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("backend")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/health", methods=["GET"])
def health():
    logger.info("Health check called")
    return jsonify({"status": "ok", "service": "backend"}), 200

@app.route("/users", methods=["GET"])
def get_users():
    logger.info("GET /users called")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    conn.close()
    users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
    return jsonify(users), 200

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}
    logger.info(f"POST /users called with data: {data}")

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": user_id, "name": name, "email": email}), 201

if __name__ == "__main__":
    init_db()
    logger.info(f"Starting backend on port {APP_PORT}")
    app.run(host="0.0.0.0", port=APP_PORT)
