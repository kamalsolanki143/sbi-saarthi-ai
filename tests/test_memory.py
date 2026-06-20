"""
SAARTHI AI — Test Suite: Memory Layer
Tests for customer_memory.py consent gating and Redis fallback.
Run: pytest tests/test_memory.py -v
"""
import pytest
from unittest.mock import MagicMock, patch


class TestCustomerMemory:

    def test_write_blocked_without_memory_consent(self):
        """update_customer_context should silently skip when memory_storage=False."""
        from backend.memory.customer_memory import CustomerMemory

        memory = CustomerMemory()

        with patch("backend.memory.customer_memory.consent_service.get_consent") as mock_consent, \
             patch("backend.memory.customer_memory.redis_memory.set_json") as mock_set:

            from backend.models.consent import ConsentRecord
            mock_consent.return_value = ConsentRecord(
                consent_id="CON-TEST",
                customer_id="CUST004",
                voice_processing=False,
                memory_storage=False,        # ← memory consent OFF
                personalized_recommendations=False,
            )

            memory.update_customer_context("CUST004", {"persona": "farmer"})
            mock_set.assert_not_called()  # Should NOT have written to Redis

    def test_write_succeeds_with_memory_consent(self):
        """update_customer_context should write when memory_storage=True."""
        from backend.memory.customer_memory import CustomerMemory
        memory = CustomerMemory()

        with patch("backend.memory.customer_memory.consent_service.get_consent") as mock_consent, \
             patch("backend.memory.customer_memory.redis_memory.get_json", return_value={}), \
             patch("backend.memory.customer_memory.redis_memory.set_json") as mock_set:

            from backend.models.consent import ConsentRecord
            mock_consent.return_value = ConsentRecord(
                consent_id="CON-TEST",
                customer_id="CUST001",
                memory_storage=True,         # ← memory consent ON
            )

            memory.update_customer_context("CUST001", {"last_agent": "margdarshan"})
            mock_set.assert_called_once()

    def test_read_always_works(self):
        """get_customer_context should never be blocked (read-only)."""
        from backend.memory.customer_memory import CustomerMemory
        memory = CustomerMemory()

        with patch("backend.memory.customer_memory.redis_memory.get_json",
                   return_value={"persona": "salaried"}):
            context = memory.get_customer_context("CUST001")
            assert context.get("persona") == "salaried"

    def test_session_clear(self):
        """clear_session should delete both customer and interaction keys."""
        from backend.memory.customer_memory import CustomerMemory
        memory = CustomerMemory()

        with patch("backend.memory.customer_memory.redis_memory.delete") as mock_delete:
            memory.clear_session("CUST001")
            assert mock_delete.call_count == 2


class TestRedisMemory:

    def test_fallback_to_dict_when_redis_unavailable(self):
        """RedisMemory should use in-memory dict when Redis is down."""
        from backend.memory.redis_memory import RedisMemory

        with patch("redis.Redis") as mock_redis:
            mock_redis.return_value.ping.side_effect = ConnectionError("Redis down")
            mem = RedisMemory()

        # Should not raise — should use fallback
        mem.set("test_key", "test_value")
        assert mem.get("test_key") == "test_value"
        assert not mem.is_available()

    def test_json_round_trip(self):
        """set_json / get_json should serialize/deserialize correctly."""
        from backend.memory.redis_memory import RedisMemory

        with patch("redis.Redis") as mock_redis:
            mock_redis.return_value.ping.side_effect = ConnectionError()
            mem = RedisMemory()

        data = {"customer_id": "CUST001", "persona": "salaried", "balance": 45000.0}
        mem.set_json("test:json", data)
        retrieved = mem.get_json("test:json")
        assert retrieved["customer_id"] == "CUST001"
        assert retrieved["persona"] == "salaried"
