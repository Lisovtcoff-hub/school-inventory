from fastapi.testclient import TestClient

from app.repositories.license_repository import create_license_code


def create_activated_tenant(client: TestClient, session_factory, *, code: str = "SCHOOL-TEST-0001") -> dict:
    with session_factory() as db:
        create_license_code(db, code=code, max_users=3, max_assets=2)
        db.commit()

    response = client.post(
        "/api/v1/auth/activate",
        json={
            "license_code": code,
            "organization_name": "Test School",
            "admin_email": "admin@example.com",
            "admin_password": "strong-password",
            "admin_full_name": "Test Administrator",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def asset_payload(*, name: str = "Classroom Laptop") -> dict:
    return {
        "type": "laptop",
        "name": name,
        "manufacturer": "Example Vendor",
        "model": "EDU-14",
        "commissioning_year": 2025,
        "room": "Computer Lab 1",
        "responsible_person": "IT Department",
        "user_category": "student",
        "status": "in_use",
        "os": "Linux",
        "report_category": "laptop",
        "is_used_for_education": True,
        "is_available_for_students": True,
        "has_lan": True,
        "has_internet": True,
        "ownership_type": "own",
    }


def test_health_endpoints(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/api/v1/health").json()["status"] == "ok"
    assert client.get("/api/v1/health/db").json()["database"] == "connected"


def test_activation_login_and_current_user(client: TestClient, session_factory) -> None:
    activated = create_activated_tenant(client, session_factory)
    headers = auth_headers(activated["access_token"])

    current = client.get("/api/v1/auth/me", headers=headers)
    assert current.status_code == 200
    assert current.json()["user"]["role"] == "admin"
    assert current.json()["organization"]["name"] == "Test School"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "strong-password"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_asset_lifecycle_history_and_license_limit(client: TestClient, session_factory) -> None:
    activated = create_activated_tenant(client, session_factory)
    headers = auth_headers(activated["access_token"])

    first = client.post("/api/v1/assets", headers=headers, json=asset_payload())
    assert first.status_code == 200, first.text
    first_asset = first.json()
    assert len(first_asset["asset_code"]) == 16
    assert first_asset["local_number"] == 1

    history = client.get(f"/api/v1/assets/{first_asset['id']}/history", headers=headers)
    assert history.status_code == 200
    assert history.json()[0]["event_type"] == "created"

    second = client.post(
        "/api/v1/assets",
        headers=headers,
        json=asset_payload(name="Library Laptop"),
    )
    assert second.status_code == 200

    over_limit = client.post(
        "/api/v1/assets",
        headers=headers,
        json=asset_payload(name="Third Laptop"),
    )
    assert over_limit.status_code == 403

    stats = client.get("/api/v1/assets/stats", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["total"] == 2
    assert stats.json()["by_type"]["laptop"] == 2

    qr = client.get(f"/api/v1/assets/{first_asset['id']}/qr.png", headers=headers)
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/png"
    assert qr.content.startswith(b"\x89PNG")

    deleted = client.delete(f"/api/v1/assets/{first_asset['id']}", headers=headers)
    assert deleted.status_code == 200
    assert client.get(f"/api/v1/assets/{first_asset['id']}", headers=headers).status_code == 404


def test_viewer_can_read_but_cannot_modify(client: TestClient, session_factory) -> None:
    activated = create_activated_tenant(client, session_factory)
    admin_headers = auth_headers(activated["access_token"])

    created_user = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "email": "viewer@example.com",
            "password": "viewer-password",
            "full_name": "Read Only User",
            "role": "viewer",
        },
    )
    assert created_user.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "viewer@example.com", "password": "viewer-password"},
    )
    viewer_headers = auth_headers(login.json()["access_token"])

    assert client.get("/api/v1/assets", headers=viewer_headers).status_code == 200
    forbidden = client.post("/api/v1/assets", headers=viewer_headers, json=asset_payload())
    assert forbidden.status_code == 403


def test_report_catalog_requires_authentication(client: TestClient, session_factory) -> None:
    assert client.get("/api/v1/reports").status_code == 401

    activated = create_activated_tenant(client, session_factory)
    response = client.get(
        "/api/v1/reports",
        headers=auth_headers(activated["access_token"]),
    )
    assert response.status_code == 200
    report_codes = {item["code"] for item in response.json()}
    assert {"OO2_SECTION_2_1", "CABINET_PASSPORT"} <= report_codes
