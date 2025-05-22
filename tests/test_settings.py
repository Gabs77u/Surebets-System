import os
from config import settings

def test_app_name():
    assert settings.APP_NAME == "Surebets Hunter Pro"

def test_debug_default():
    assert settings.DEBUG is False

def test_port_default():
    assert settings.PORT == 8050
