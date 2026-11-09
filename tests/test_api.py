def test_create_lead_assigns_priority_and_persists_it(client):
    response = client.post(
        "/leads",
        json={
            "source": "avito",
            "text": "Need a sofa ASAP",
            "amount": 1000,
            "created_at": "2026-11-09T19:00:00+03:00",
        },
    )

    assert response.status_code == 201
    created_lead = response.json()
    assert created_lead["priority"] == "high"

    saved_response = client.get(f"/leads/{created_lead['id']}")
    assert saved_response.status_code == 200
    assert saved_response.json()["id"] == created_lead["id"]
    assert saved_response.json()["priority"] == "high"


def test_list_leads_filters_and_orders_by_priority(client):
    low_response = client.post(
        "/leads",
        json={
            "source": "avito",
            "text": "Нужна тумба",
            "amount": 1000,
            "created_at": "2026-11-09T19:00:00+03:00",
        },
    )
    high_response = client.post(
        "/leads",
        json={
            "source": "site",
            "text": "Нужен диван",
            "amount": 100000,
            "created_at": "2026-11-09T19:01:00+03:00",
        },
    )

    assert low_response.status_code == 201
    assert high_response.status_code == 201

    all_leads = client.get("/leads")
    assert all_leads.status_code == 200
    assert [lead["priority"] for lead in all_leads.json()] == ["high", "low"]

    high_leads = client.get("/leads?priority=high")
    assert high_leads.status_code == 200
    assert [lead["id"] for lead in high_leads.json()] == [high_response.json()["id"]]


def test_create_lead_rejects_blank_text(client):
    response = client.post(
        "/leads",
        json={"source": "site", "text": "   ", "amount": 1000},
    )

    assert response.status_code == 422


def test_create_lead_rejects_unknown_source(client):
    response = client.post(
        "/leads",
        json={"source": "email", "text": "Нужен диван", "amount": 1000},
    )

    assert response.status_code == 422


def test_create_lead_rejects_datetime_without_timezone(client):
    response = client.post(
        "/leads",
        json={
            "source": "site",
            "text": "Нужен диван",
            "created_at": "2026-11-09T10:00:00",
        },
    )

    assert response.status_code == 422
