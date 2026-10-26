from backend import config


def test_cloud_database_urls_are_normalised():
    n = config.normalize_db_url
    assert n("postgres://u:p@host/db") == "postgresql+psycopg2://u:p@host/db"
    assert n("postgresql://u:p@host/db?sslmode=require") == "postgresql+psycopg2://u:p@host/db?sslmode=require"
    assert n("postgresql+psycopg2://u:p@host/db") == "postgresql+psycopg2://u:p@host/db"  # already fine
    assert n("sqlite:///./data/x.db").startswith("sqlite:////")  # made absolute


def test_writes_open_when_no_api_key(client):
    assert client.post("/parking/entry", json={"vehicle_number": "MH12AB1234"}).status_code == 201


def test_writes_need_api_key_when_configured(client, monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "secret-123")
    body = {"vehicle_number": "MH12AB1234"}
    assert client.post("/parking/entry", json=body).status_code == 401
    assert client.post("/parking/entry", json=body, headers={"X-API-Key": "wrong"}).status_code == 401
    ok = client.post("/parking/entry", json=body, headers={"X-API-Key": "secret-123"})
    assert ok.status_code == 201
    assert client.post("/parking/exit", json=body).status_code == 401
    assert client.post("/parking/exit", json=body, headers={"X-API-Key": "secret-123"}).status_code == 200


def test_reading_stays_open_with_api_key(client, monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "secret-123")
    assert client.get("/parking/status").status_code == 200
    assert client.get("/health").status_code == 200
