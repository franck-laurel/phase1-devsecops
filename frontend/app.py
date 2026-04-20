from flask import Flask, request, render_template_string, redirect
import requests
import os
import logging

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
APP_PORT = int(os.getenv("APP_PORT", 5001))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("frontend")

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Frontend</title>
</head>
<body>
    <h1>Liste des utilisateurs</h1>
    <form method="POST" action="/add-user">
        <input type="text" name="name" placeholder="Nom" required>
        <input type="email" name="email" placeholder="Email" required>
        <button type="submit">Ajouter</button>
    </form>
    <hr>
    <ul>
    {% for user in users %}
        <li>{{ user["id"] }} - {{ user["name"] }} - {{ user["email"] }}</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    logger.info("GET / called")
    try:
        response = requests.get(f"{API_URL}/users", timeout=5)
        users = response.json()
    except Exception as e:
        logger.error(f"Error contacting backend: {e}")
        users = []
    return render_template_string(HTML_PAGE, users=users)

@app.route("/add-user", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")
    logger.info(f"POST /add-user name={name} email={email}")
    try:
        requests.post(
            f"{API_URL}/users",
            json={"name": name, "email": email},
            timeout=5
        )
    except Exception as e:
        logger.error(f"Error sending data to backend: {e}")
    return redirect("/")

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "frontend"}, 200

if __name__ == "__main__":
    logger.info(f"Starting frontend on port {APP_PORT}")
    app.run(host="0.0.0.0", port=APP_PORT)
