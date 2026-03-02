import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# --- GET /activities ---
def test_get_activities():
    # Arrange: nothing to set up, just use the client
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

# --- POST /activities/{activity}/signup ---
def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "successfully" in data["message"].lower()
    # Clean up: remove the participant for idempotency
    client.delete(f"/activities/{activity}/signup?email={email}")

def test_signup_duplicate():
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()

def test_signup_full():
    # Arrange
    activity = "Chess Club"
    # Remplir l'activité
    for i in range(20):
        client.post(f"/activities/{activity}/signup?email=full{i}@mergington.edu")
    # Act
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "full" in data["detail"].lower()
    # Clean up
    for i in range(20):
        client.delete(f"/activities/{activity}/signup?email=full{i}@mergington.edu")
    client.delete(f"/activities/{activity}/signup?email=overflow@mergington.edu")

# --- DELETE /activities/{activity}/signup ---
def test_delete_participant():
    # Arrange
    email = "todelete@mergington.edu"
    activity = "Programming Class"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "removed" in data["message"].lower()

def test_delete_nonexistent_participant():
    # Arrange
    email = "notfound@mergington.edu"
    activity = "Programming Class"
    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

# --- Error cases ---
def test_signup_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_signup_missing_email():
    # Arrange
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup")
    # Assert
    assert response.status_code == 422  # FastAPI validation error
