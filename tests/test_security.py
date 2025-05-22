from config import security

def test_generate_hash():
    h1 = security.generate_hash("abc")
    h2 = security.generate_hash("abc")
    assert h1 == h2
    assert isinstance(h1, str)
