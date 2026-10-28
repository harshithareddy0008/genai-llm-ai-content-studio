"""FastAPI endpoints and validation without external network calls."""


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").status_code == 200


def test_generate_email(client, auth_headers):
    response = client.post("/generate", json={
        "task": "email", "input_text": "Request internship",
        "tone": "friendly", "length": "short", "temperature": 0.3,
    }, headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["task"] == "email"
    assert "Mock email" in data["generated_text"]
    assert data["model"] == "fake-gemini-test-model"


def test_generate_all_five_tasks(client, auth_headers):
    for task in ["email", "linkedin", "summary", "rewrite", "blog"]:
        response = client.post("/generate", json={
            "task": task, "input_text": "An example input topic"
        }, headers=auth_headers)
        assert response.status_code == 200, (task, response.text)


def test_rejects_short_input(client, auth_headers):
    response = client.post("/generate", json={
        "task": "blog", "input_text": "  "
    }, headers=auth_headers)
    assert response.status_code == 422


def test_rejects_unknown_task(client, auth_headers):
    response = client.post("/generate", json={
        "task": "agent", "input_text": "Some research task"
    }, headers=auth_headers)
    assert response.status_code == 422


def test_rejects_invalid_temperature(client, auth_headers):
    response = client.post("/generate", json={
        "task": "email", "input_text": "Write a letter", "temperature": 2.0
    }, headers=auth_headers)
    assert response.status_code == 422


def test_rejects_unexpected_request_keys(client, auth_headers):
    response = client.post("/generate", json={
        "task": "email", "input_text": "Write a letter", "system_override": "ignore rules"
    }, headers=auth_headers)
    assert response.status_code == 422


def test_chat_with_context(client, auth_headers):
    response = client.post("/chat", json={
        "message": "And what next?",
        "history": [
            {"role": "user", "content": "I built an ML app"},
            {"role": "assistant", "content": "Great work!"},
        ],
    }, headers=auth_headers)
    assert response.status_code == 200
    assert "And what next?" in response.json()["reply"]


def test_chat_rejects_more_than_12_history_messages(client, auth_headers):
    response = client.post("/chat", json={
        "message": "Hi", "history": [{"role": "user", "content": "Hi"}] * 13
    }, headers=auth_headers)
    assert response.status_code == 422


def test_protected_endpoints_require_shared_token(client):
    assert client.post("/generate", json={
        "task": "email", "input_text": "Write an email"
    }).status_code == 401
    assert client.post("/chat", json={"message": "Hello"}).status_code == 401
    assert client.get("/health").status_code == 200
