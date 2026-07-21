from django.db import connection


def test_v2_is_configured_for_postgresql():
    assert connection.vendor == "postgresql"
