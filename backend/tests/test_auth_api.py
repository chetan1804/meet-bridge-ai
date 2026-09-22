from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_db_session() -> Generator[Session, None, None]:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db_session] = override_db_session
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_registration_login_and_current_user() -> None:
    credentials = {"email": "person@example.com", "password": "a-long-secret-password"}

    registration = client.post("/api/auth/register", json=credentials)
    assert registration.status_code == 201
    token = registration.json()["access_token"]

    current_user = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current_user.status_code == 200
    assert current_user.json()["email"] == credentials["email"]

    login = client.post("/api/auth/login", json=credentials)
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_auth_rejects_duplicate_invalid_and_missing_credentials() -> None:
    credentials = {"email": "person@example.com", "password": "a-long-secret-password"}
    assert client.post("/api/auth/register", json=credentials).status_code == 201
    assert client.post("/api/auth/register", json=credentials).status_code == 409
    assert client.post("/api/auth/login", json={**credentials, "password": "wrong-password-value"}).status_code == 401
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.value"}).status_code == 401
