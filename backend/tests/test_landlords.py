def test_create_landlord(client):
    payload = {
        "full_name": "John Banda",
        "national_id": "63-1234567A89",
        "phone": "0772123456",
        "email": "john@example.com",
        "address": "12 Main St, Harare",
        "bank_details": "CBZ 1234567890"
    }
    resp = client.post("/api/v1/landlords/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "John Banda"
    assert data["phone"] == "0772123456"
