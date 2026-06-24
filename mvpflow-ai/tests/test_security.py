"""Auth-layer tests: password hashing and JWT create/verify."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.security import security_manager


def test_password_hash_and_verify():
    hashed = security_manager.hash_password("s3cret")
    assert hashed != "s3cret"
    assert security_manager.verify_password("s3cret", hashed)
    assert not security_manager.verify_password("wrong", hashed)


def test_jwt_roundtrip():
    token = security_manager.create_access_token("user-123")
    payload = security_manager.verify_token(token)
    assert payload["sub"] == "user-123"


def test_verify_token_rejects_garbage():
    with pytest.raises(HTTPException) as exc:
        security_manager.verify_token("not-a-real-token")
    assert exc.value.status_code == 401


def test_optional_user_none_without_credentials():
    # The optional-auth dependency must resolve to None when no token is given.
    assert security_manager.get_optional_user(None) is None
