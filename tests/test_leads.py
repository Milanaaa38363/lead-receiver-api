import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base
from app.config import API_TOKEN

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_unauthorized():
    response = client.post("/leads", json={"name": "Тест", "phone": "+77015550009", "source": "web"})
    assert response.status_code == 401

def test_deduplication():
    headers = {"X-Token": API_TOKEN}

    resp1 = client.post("/leads", headers=headers, json={
        "name": "Аружан",
        "phone": "+7 701 555-00-09",
        "source": "instagram"
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["is_new_client"] is True

    resp2 = client.post("/leads", headers=headers, json={
        "name": "Аружан",
        "phone": "8 (701) 555 00 09",
        "source": "website"
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["is_new_client"] is False
    assert data2["client_id"] == data1["client_id"]
    assert data2["deal_id"] == data1["deal_id"]

def test_invalid_phone():
    headers = {"X-Token": API_TOKEN}
    resp = client.post("/leads", headers=headers, json={
        "name": "Иван",
        "phone": "123",
        "source": "site"
    })
    assert resp.status_code == 422