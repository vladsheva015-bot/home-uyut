import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main_module
from app.database import Base


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    """Return an API client backed by a fresh in-memory test database."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    def override_get_db():
        db: Session = test_session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(main_module, "engine", test_engine)
    main_module.app.dependency_overrides[main_module.get_db] = override_get_db

    with TestClient(main_module.app) as test_client:
        yield test_client

    main_module.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)