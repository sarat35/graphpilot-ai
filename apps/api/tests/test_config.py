from app.config.settings import settings


def test_app_name():
    assert settings.app_name == "buyseconds"


def test_environment():
    assert settings.app_env == "development"
