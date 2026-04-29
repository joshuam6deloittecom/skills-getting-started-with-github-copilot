import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    # Arrange: No special setup needed

    # Act: Make GET request to root
    response = client.get("/")

    # Assert: Should redirect to /static/index.html
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange: No special setup needed

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Should return 200 and the activities dict
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    # Arrange: Choose an activity and a new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 200 and success message
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_activity_not_found():
    # Arrange: Use a non-existent activity
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 404 with error detail
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_email():
    # Arrange: Sign up first, then try again
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    # First signup (success)
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to signup again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Should return 400 with error detail
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]