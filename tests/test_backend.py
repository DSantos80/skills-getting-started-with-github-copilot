from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "michael@mergington.edu" in payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_student(client):
    student_email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup?email=" + student_email)

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {student_email} for Chess Club"
    }
    assert student_email in activities["Chess Club"]["participants"]


def test_signup_for_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_enrollment(client):
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_unregister_for_activity_removes_student(client):
    student_email = "michael@mergington.edu"

    response = client.delete("/activities/Chess%20Club/signup?email=" + student_email)

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {student_email} from Chess Club"
    }
    assert student_email not in activities["Chess Club"]["participants"]


def test_unregister_for_missing_student_returns_404(client):
    response = client.delete("/activities/Chess%20Club/signup?email=notregistered@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
