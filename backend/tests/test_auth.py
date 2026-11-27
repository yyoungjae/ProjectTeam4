SIGNUP = {"email": "a@test.com", "password": "password123", "nickname": "한결"}


def signup(client, **override):
    return client.post("/api/auth/signup", json={**SIGNUP, **override})


def login(client, email="a@test.com", password="password123"):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_signup_success(client):
    res = signup(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "a@test.com"
    assert body["nickname"] == "한결"
    assert "password_hash" not in body  # 비밀번호 해시가 응답에 나가면 안 됨


def test_signup_duplicate_email(client):
    signup(client)
    res = signup(client, nickname="다른닉")
    assert res.status_code == 409
    assert res.json()["code"] == "EMAIL_TAKEN"


def test_signup_duplicate_nickname(client):
    signup(client)
    res = signup(client, email="b@test.com")
    assert res.status_code == 409
    assert res.json()["code"] == "NICKNAME_TAKEN"


def test_signup_short_password(client):
    res = signup(client, password="123")
    assert res.status_code == 400
    assert res.json()["code"] == "VALIDATION_ERROR"


def test_login_success(client):
    signup(client)
    res = login(client)
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"]


def test_login_wrong_password(client):
    signup(client)
    res = login(client, password="wrong-password")
    assert res.status_code == 401
    assert res.json()["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email(client):
    res = login(client, email="nobody@test.com")
    assert res.status_code == 401
    assert res.json()["code"] == "INVALID_CREDENTIALS"
