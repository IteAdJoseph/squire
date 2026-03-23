from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    hashed = hash_password("minha-senha")
    assert verify_password("minha-senha", hashed)
    assert not verify_password("senha-errada", hashed)


def test_token_roundtrip() -> None:
    token = create_access_token("user-abc", "tenant-xyz")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["tenant_id"] == "tenant-xyz"
