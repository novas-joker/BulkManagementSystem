from app.schemas.contact import ContactCreateRequest, ContactResponse, ContactUpdateRequest


def test_contact_create_schema_validation():
    payload = ContactCreateRequest(
        email="contact@example.com",
        first_name="Jane",
        last_name="Doe",
        custom_fields={"company": "Acme"},
    )

    assert payload.email == "contact@example.com"
    assert payload.first_name == "Jane"
    assert payload.status == "subscribed"


def test_contact_update_schema_validation():
    payload = ContactUpdateRequest(
        first_name="John",
        status="unsubscribed",
    )

    assert payload.first_name == "John"
    assert payload.status == "unsubscribed"


def test_contact_response_model():
    model = ContactResponse(
        id="contact-1",
        user_id="user-1",
        email="contact@example.com",
        first_name="Jane",
        last_name="Doe",
        status="subscribed",
        source="manual",
        custom_fields={"company": "Acme"},
        is_valid_email=True,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00",
    )

    assert model.email == "contact@example.com"
    assert model.full_name == "Jane Doe"
