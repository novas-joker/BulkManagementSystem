from app.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
)


def test_auth_register_schema_validation():
    payload = UserRegisterRequest(
        email="user@example.com",
        password="StrongPass123!",
        full_name="Test User",
    )

    assert payload.email == "user@example.com"
    assert payload.full_name == "Test User"


def test_auth_login_schema_validation():
    payload = UserLoginRequest(
        email="user@example.com",
        password="StrongPass123!",
    )

    assert payload.email == "user@example.com"
    assert payload.password == "StrongPass123!"


def test_token_response_model():
    token = TokenResponse(
        access_token="abc123",
        token_type="bearer",
        user={
            "id": "123",
            "email": "user@example.com",
            "full_name": "Test User",
            "role": "user",
        },
    )

    assert token.access_token == "abc123"
    assert token.token_type == "bearer"
    assert token.user.email == "user@example.com"


def test_user_profile_response_model():
    profile = {
        "id": "123",
        "email": "user@example.com",
        "full_name": "Test User",
        "role": "user",
        "status": "active",
    }

    model = UserProfileResponse(**profile)

    assert model.email == "user@example.com"
    assert model.status == "active"
