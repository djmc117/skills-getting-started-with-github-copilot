from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Mergington High School" in response.text


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_adds_participant_to_activity():
    email = "test_student@mergington.edu"
    activity_name = "Chess Club"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    email = "duplicate_student@mergington.edu"
    activity_name = "Programming Class"

    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    email = "remove_student@mergington.edu"
    activity_name = "Gym Class"

    client.post(f"/activities/{activity_name}/signup?email={email}")
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_remove_missing_participant_returns_400():
    email = "missing_student@mergington.edu"
    activity_name = "Art Club"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found for this activity"
