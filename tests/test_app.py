from urllib.parse import quote


def activity_url(activity_name: str, suffix: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/{suffix}"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_data_and_cache_headers(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"

    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_student(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(activity_url(activity_name, "signup"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    updated_payload = client.get("/activities").json()
    assert email in updated_payload[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicates(client):
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(activity_url(activity_name, "signup"), params={"email": existing_email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_for_activity_returns_not_found_for_unknown_activity(client):
    response = client.post(activity_url("Robotics Club", "signup"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_removes_student(client):
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"

    response = client.delete(activity_url(activity_name, "participants"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

    updated_payload = client.get("/activities").json()
    assert email not in updated_payload[activity_name]["participants"]


def test_unregister_from_activity_returns_not_found_for_missing_student(client):
    activity_name = "Basketball Team"

    response = client.delete(
        activity_url(activity_name, "participants"),
        params={"email": "unknown@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}


def test_unregister_from_activity_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        activity_url("Robotics Club", "participants"),
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
