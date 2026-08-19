from app.core.security import decrypt_secret, encrypt_secret
from app.infrastructure.email.providers import EmailProviderFactory, MockEmailProvider, SMTPProvider, ZeptoMailProvider


def test_secret_encryption_round_trip():
    value = "super-secret-provider-token"
    encrypted = encrypt_secret(value)

    assert encrypted != value
    assert decrypt_secret(encrypted) == value


def test_mock_provider_sends_email_successfully():
    provider = MockEmailProvider()

    result = provider.send(
        to_email="user@example.com",
        subject="Welcome",
        body="Hello from MailForge",
        from_email="noreply@example.com",
    )

    assert result.success is True
    assert result.provider == "mock"
    assert result.status == "sent"
    assert result.to_email == "user@example.com"


def test_factory_returns_expected_provider_for_mail_route():
    zepto = EmailProviderFactory.get_provider("zeptomail")
    smtp = EmailProviderFactory.get_provider("smtp")

    assert isinstance(zepto, ZeptoMailProvider)
    assert isinstance(smtp, SMTPProvider)

    default_provider = EmailProviderFactory.get_provider()
    assert isinstance(default_provider, ZeptoMailProvider)
