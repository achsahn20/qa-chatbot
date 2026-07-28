def test_signup_and_get_profile(client):
    signup = client.post(
        "/api/v1/auth/signup",
        json={"full_name": "Alice Example", "email": "alice@example.com", "password": "Password123"},
    )
    assert signup.status_code == 201
    token = signup.json()["access_token"]

    profile = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["email"] == "alice@example.com"


def test_login_with_invalid_password_returns_401(client):
    client.post(
        "/api/v1/auth/signup",
        json={"full_name": "Bob Example", "email": "bob@example.com", "password": "Password123"},
    )

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "bob@example.com", "password": "wrongpass1"},
    )
    assert login.status_code == 401
