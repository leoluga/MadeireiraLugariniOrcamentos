# tests/test_endpoints.py

import pytest
from fastapi.testclient import TestClient

def test_create_wood_endpoint(client: TestClient):
    response = client.post(
        "/wood",
        headers={"x-user-role": "ADMIN_SELLER"},  # or SELLER
        json={
            "name": "Itauba",
            "price_per_volume": 15.0
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert data["name"] == "Itauba"
    assert data["price_per_volume"] == 15.0

def test_create_orcamento_endpoint(client: TestClient):
    # 1) Create a wood
    r = client.post(
        "/wood",
        headers={"x-user-role": "ADMIN_SELLER"},
        json={"name": "Cedrinho", "price_per_volume": 10}
    )
    assert r.status_code == 200, r.text
    wood_data = r.json()
    wood_id = wood_data["id"]

    # 2) Create an orcamento with that wood
    r2 = client.post("/orcamento", json={
        "items": [
            {
                "wood_id": wood_id,
                "length": 4,
                "width": 1,
                "height": 3,
                "quantity": 4
            }
        ]
    })
    assert r2.status_code == 200, r2.text
    orc_data = r2.json()
    assert "orcamento_id" in orc_data
    assert "final_price" in orc_data

def test_apply_discount_endpoint(client: TestClient):
    # 1) Create wood
    r = client.post(
        "/wood",
        headers={"x-user-role": "ADMIN_SELLER"},
        json={"name": "Pau-Brasil", "price_per_volume": 20}
    )
    assert r.status_code == 200, r.text
    wood_id = r.json()["id"]

    # 2) Create orcamento
    r2 = client.post("/orcamento", json={
        "items": [
            {
                "wood_id": wood_id, 
                "length": 2, 
                "width":2, 
                "height":1, 
                "quantity":2
            }
        ]
    })
    assert r2.status_code == 200, r2.text
    orc_data = r2.json()
    orc_id = orc_data["orcamento_id"]
    base_price = orc_data["final_price"]

    # 3) Apply discount as admin
    r3 = client.post("/orcamento/discount", json={
        "orcamento_id": orc_id,
        "discount": 5.0,
        "user_role": "ADMIN_SELLER"
    })
    assert r3.status_code == 200, r3.text
    disc_data = r3.json()
    assert disc_data["final_price"] == base_price - 5.0
    assert disc_data["discount_applied"] == 5.0

    # 4) Non-admin => fails
    r4 = client.post("/orcamento/discount", json={
        "orcamento_id": orc_id,
        "discount": 5.0,
        "user_role": "SELLER"
    })
    assert r4.status_code == 403, r4.text
    assert "detail" in r4.json()
