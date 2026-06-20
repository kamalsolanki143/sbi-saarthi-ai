"""
SAARTHI AI — Test Suite: API Routes
Integration tests using FastAPI TestClient.
Run: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    from backend.main import app
    return TestClient(app)


class TestHealthEndpoints:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "SAARTHI AI" in response.json()["message"]


class TestCustomerRoutes:
    def test_get_existing_customer(self, client):
        response = client.get("/customers/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST001"
        assert "mpin_hash" not in data  # MPIN must never leak!

    def test_get_nonexistent_customer_returns_404(self, client):
        response = client.get("/customers/CUST999")
        assert response.status_code == 404
        assert response.json()["error_code"] == "CUSTOMER_NOT_FOUND"

    def test_create_customer(self, client):
        payload = {
            "name": "Test User",
            "phone": "9999988888",
            "account_type": "savings",
        }
        with patch("backend.routes.customer.repo.insert"), \
             patch("backend.services.event_engine.event_engine.classify_and_create"):
            response = client.post("/customers", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert "mpin_hash" not in data

    def test_get_persona(self, client):
        with patch("backend.routes.customer.persona_engine.classify") as mock_classify, \
             patch("backend.routes.customer.repo.find_by_field", return_value=[]), \
             patch("backend.routes.customer.repo.upsert"):
            from backend.models.customer import PersonaType
            mock_classify.return_value = PersonaType.SALARIED
            response = client.get("/customers/CUST001/persona")
        assert response.status_code == 200
        assert response.json()["persona"] == "salaried"


class TestConsentRoutes:
    def test_get_consent(self, client):
        response = client.get("/consent/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert "voice_processing" in data
        assert "memory_storage" in data
        assert "personalized_recommendations" in data

    def test_grant_consent(self, client):
        payload = {"voice_processing": True, "memory_storage": True}
        response = client.post("/consent/CUST001/grant", json=payload)
        assert response.status_code == 200
        assert response.json()["voice_processing"] is True


class TestEventRoutes:
    def test_receive_salary_credit_event(self, client):
        with patch("backend.routes.event.dispatch") as mock_dispatch:
            from backend.models.recommendation import Recommendation, ActionPreview, ProductType, RecommendationStatus
            from datetime import datetime, timezone
            mock_rec = MagicMock()
            mock_rec.recommendation_id = "REC-TEST001"
            mock_rec.title = "Open FD"
            mock_dispatch.return_value = mock_rec
            mock_dispatch.return_value = mock_rec

            payload = {
                "customer_id": "CUST001",
                "event_type": "salary_credit",
                "amount": 55000.0,
                "source": "webhook",
            }
            response = client.post("/events", json=payload)

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert "event_id" in data

    def test_invalid_event_type_returns_422(self, client):
        payload = {
            "customer_id": "CUST001",
            "event_type": "invalid_event_type",
            "source": "webhook",
        }
        response = client.post("/events", json=payload)
        assert response.status_code == 422  # Pydantic validation error


class TestAuditRoutes:
    def test_get_audit_trail(self, client):
        response = client.get("/audit/CUST001")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total_entries" in data

    def test_get_live_feed(self, client):
        response = client.get("/audit/live/CUST001?last_n=5")
        assert response.status_code == 200
