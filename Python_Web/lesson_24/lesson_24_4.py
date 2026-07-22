import pytest
from lesson_24_3 import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_success(client):
    response = client.post(
        '/login',
        json={"username": "admin", "password": "secret"}
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Login successful"}


def test_login_invalid_credentials(client):
    response = client.post(
        '/login',
        json={"username": "admin", "password": "wrong_password"}
    )

    assert response.status_code == 401
    assert response.get_json() == {"message": "Invalid credentials"}