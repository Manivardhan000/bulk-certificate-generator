def test_create_generation_job(client):
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "certificate_title": "Certificate of Completion",
            "recipients": [
                {"name": "Abhinav Sai", "email": "abhinav@example.com"},
                {"name": "Rahul Kumar", "email": "rahul@example.com"},
            ],
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert body["total_count"] == 2
    assert body["status"] == "PENDING"
    assert body["progress"] == 0.0


def test_invalid_email_is_rejected(client):
    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "recipients": [{"name": "Abhinav", "email": "not-an-email"}],
        },
    )
    assert response.status_code == 422


def test_job_not_found(client):
    response = client.get("/api/jobs/does-not-exist")
    assert response.status_code == 404


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
