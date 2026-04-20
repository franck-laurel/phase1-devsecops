import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "backend"
