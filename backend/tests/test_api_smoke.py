from fastapi.testclient import TestClient

from app.main import app
from scripts.seed_pilot import seed


def test_health_endpoint():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}


def test_search_and_public_shop_endpoints():
    seed()
    client = TestClient(app)

    search = client.get("/v1/shops/search", params={"q": "tailor", "pin": "560103"})
    assert search.status_code == 200
    payload = search.json()
    assert payload["total"] >= 1

    detail = client.get("/v1/shops/public/rajutailor@upi")
    assert detail.status_code == 200
    shop = detail.json()
    assert shop["display_name"] == "Raju Tailor"
    assert len(shop["services"]) >= 1
