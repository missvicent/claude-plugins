from src import store
from src.checks import expired_status, never_reused


def test_deleted_code_is_never_reused():
    store.add("abc", "https://example.com")
    store.delete("abc")
    assert never_reused("abc") is False


def test_expired_returns_410():
    assert expired_status(True) == 410
