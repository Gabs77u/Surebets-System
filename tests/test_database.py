from backend.database.database import SimpleCache

def test_cache_set_and_get():
    cache = SimpleCache()
    cache.set("key", 123)
    assert cache.get("key") == 123

def test_cache_clear():
    cache = SimpleCache()
    cache.set("key", 123)
    cache.clear()
    assert cache.get("key") is None
