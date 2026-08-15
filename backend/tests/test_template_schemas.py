from app.schemas.template import TemplateCreateRequest, TemplateResponse, TemplateUpdateRequest


def test_template_create_schema_validation():
    payload = TemplateCreateRequest(
        name="Welcome Email",
        subject="Welcome!",
        html_content="<h1>Hello</h1>",
        plain_text_content="Hello",
        template_type="standard",
        template_variables=["first_name", "company"],
    )

    assert payload.name == "Welcome Email"
    assert payload.subject == "Welcome!"
    assert payload.template_type == "standard"


def test_template_update_schema_validation():
    payload = TemplateUpdateRequest(
        subject="Updated Welcome",
        is_active=False,
    )

    assert payload.subject == "Updated Welcome"
    assert payload.is_active is False


def test_template_response_model():
    model = TemplateResponse(
        id="template-1",
        user_id="user-1",
        name="Welcome Email",
        subject="Welcome!",
        html_content="<h1>Hello</h1>",
        plain_text_content="Hello",
        preview_text="Preview",
        template_type="standard",
        template_variables=["first_name"],
        is_active=True,
        usage_count=0,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00",
    )

    assert model.name == "Welcome Email"
    assert model.is_active is True
