from tests.test_auth import login, signup


def test_me_without_token(client):
    res = client.get("/api/users/me")
    assert res.status_code == 401
    assert res.json()["code"] == "UNAUTHORIZED"


def test_me_with_token(client):
    signup(client)
    token = login(client).json()["access_token"]
    res = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "a@test.com"


def test_me_with_fake_token(client):
    res = client.get("/api/users/me", headers={"Authorization": "Bearer fake.token.value"})
    assert res.status_code == 401

def _auth(client):
    signup(client)
    token = login(client).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_nickname(client):
    headers = _auth(client)
    res = client.patch("/api/users/me", json={"nickname": "새닉네임"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["nickname"] == "새닉네임"
    assert client.get("/api/users/me", headers=headers).json()["nickname"] == "새닉네임"


def test_update_setting_only_keeps_nickname(client):
    headers = _auth(client)
    res = client.patch("/api/users/me", json={"delete_video_after_analysis": True}, headers=headers)
    assert res.status_code == 200
    assert res.json()["delete_video_after_analysis"] is True
    assert res.json()["nickname"] == "한결"  # 안 보낸 필드는 그대로


def test_update_nickname_taken(client):
    signup(client, email="b@test.com", nickname="남의닉")
    headers = _auth(client)
    res = client.patch("/api/users/me", json={"nickname": "남의닉"}, headers=headers)
    assert res.status_code == 409
    assert res.json()["code"] == "NICKNAME_TAKEN"


def test_update_without_token(client):
    res = client.patch("/api/users/me", json={"nickname": "새닉네임"})
    assert res.status_code == 401