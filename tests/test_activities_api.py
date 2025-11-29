import pytest

from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants for restoration after test
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    for k, v in original.items():
        activities[k]["participants"] = v[:]


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)

    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure user not already in participants
    assert email not in activities[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    # Signup again should return 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp3.status_code == 200
    assert resp3.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]

    # Unregister again should return 400
    resp4 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp4.status_code == 400
