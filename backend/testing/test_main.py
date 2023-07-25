from fastapi.testclient import TestClient

import sys
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


from main import app

client = TestClient(app)


def test_index():
    response = client.get("/index")
    assert response.status_code == 200
    assert response.json() == {"msg": "Ok!"}


def test_old():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Ok!"}
