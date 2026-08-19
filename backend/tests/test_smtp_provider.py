from app.infrastructure.email.providers.smtp import SMTPProvider


def test_smtp_provider_sends_via_smtp(monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port):
            calls["init"] = (host, port)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def starttls(self):
            calls["starttls"] = True

        def login(self, username, password):
            calls["login"] = (username, password)

        def send_message(self, message):
            calls["message"] = message
            return {}

        def quit(self):
            calls["quit"] = True

    monkeypatch.setattr("app.infrastructure.email.providers.smtp.smtplib.SMTP", FakeSMTP)

    provider = SMTPProvider(
        host="smtp.gmail.com",
        port=587,
        username="sender@gmail.com",
        password="secret-password",
    )

    result = provider.send(
        to_email="user@example.com",
        subject="Test subject",
        body="<p>Hello</p>",
        from_email="sender@gmail.com",
        metadata={"template_id": "tpl-123"},
    )

    assert result.success is True
    assert result.status == "sent"
    assert calls["login"] == ("sender@gmail.com", "secret-password")
    assert calls["message"]["To"] == "user@example.com"
    assert calls["message"]["Subject"] == "Test subject"
