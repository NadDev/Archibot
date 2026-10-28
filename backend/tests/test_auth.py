from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from gotrue.types import User, UserResponse

from app import auth
from app.config import Settings


def test_current_user_requires_bearer_credentials() -> None:
    with pytest.raises(HTTPException) as error:
        auth.get_current_user(None)

    assert error.value.status_code == 401
    assert error.value.headers == {"WWW-Authenticate": "Bearer"}


def test_current_user_validates_token_with_supabase(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, str]] = []

    class FakeAuth:
        def get_user(self, *, jwt: str) -> UserResponse:
            calls.append(("get_user", jwt, ""))
            return UserResponse(user=User(
                id="user-123", aud="authenticated", app_metadata={}, user_metadata={},
                created_at=datetime.fromisoformat("2026-10-28T00:00:00+00:00"),
            ))

    class FakeClient:
        auth = FakeAuth()

    def fake_create_client(url: str, key: str) -> FakeClient:
        calls.append((url, key, "create_client"))
        return FakeClient()

    monkeypatch.setattr(auth, "create_client", fake_create_client)
    monkeypatch.setattr(
        auth,
        "get_settings",
        lambda: Settings(
            supabase_url="https://example.supabase.co",
            supabase_publishable_key="test-publishable-key",
            chunks_table="chunks",
            embedding_model="test-model",
        ),
    )

    user = auth.get_current_user(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="user-token")
    )

    assert user == auth.AuthenticatedUser(id="user-123", access_token="user-token")
    assert calls == [
        ("https://example.supabase.co", "test-publishable-key", "create_client"),
        ("get_user", "user-token", ""),
    ]


def test_current_user_fails_closed_without_supabase_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        auth,
        "get_settings",
        lambda: Settings(
            supabase_url=None,
            supabase_publishable_key=None,
            chunks_table="chunks",
            embedding_model="test-model",
        ),
    )

    with pytest.raises(HTTPException) as error:
        auth.get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="user-token")
        )

    assert error.value.status_code == 503


def test_current_user_rejects_empty_auth_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(auth, "get_settings", lambda: Settings("https://example.supabase.co", "test-key", "chunks", "test-model"))
    monkeypatch.setattr(auth, "create_client", lambda *args: SimpleNamespace(
        auth=SimpleNamespace(get_user=lambda **kwargs: SimpleNamespace(user=None)),
    ))
    with pytest.raises(HTTPException) as error:
        auth.get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="user-token"))
    assert error.value.status_code == 401