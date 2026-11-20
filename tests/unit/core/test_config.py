from app.core.config import get_settings


def test_settings_have_expected_defaults() -> None:
    settings = get_settings()

    assert settings.app_name == "Raglicious: AI Chatbot API"
    assert settings.app_version == "1.0.0"
    assert settings.environment == "development"
