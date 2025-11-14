from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity checks for a few known activities
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "test_user@example.com"

    # Ensure email not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    participants = data[activity]["participants"]
    if test_email in participants:
        # cleanup if previous runs left it behind
        del_resp = client.delete(f"/activities/{activity}/participants?email={test_email}")
        assert del_resp.status_code == 200

    # Sign up
    signup_resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert signup_resp.status_code == 200
    signup_json = signup_resp.json()
    assert "Signed up" in signup_json.get("message", "")

    # Verify participant present
    resp_after = client.get("/activities")
    assert resp_after.status_code == 200
    data_after = resp_after.json()
    assert test_email in data_after[activity]["participants"]

    # Unregister
    del_resp = client.delete(f"/activities/{activity}/participants?email={test_email}")
    assert del_resp.status_code == 200
    del_json = del_resp.json()
    assert "Unregistered" in del_json.get("message", "")

    # Verify removal
    final = client.get("/activities")
    assert final.status_code == 200
    final_data = final.json()
    assert test_email not in final_data[activity]["participants"]
