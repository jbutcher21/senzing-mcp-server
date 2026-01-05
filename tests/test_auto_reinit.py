"""Tests for auto-reinitialization on stale config errors."""

import asyncio
import json
import sys
from unittest.mock import MagicMock, AsyncMock, patch

import pytest


# Mock the senzing imports before importing our module
sys.modules['senzing'] = MagicMock()
sys.modules['senzing_core'] = MagicMock()

# Now we can import our module
from senzing_mcp.sdk_wrapper import SenzingSDKWrapper, STALE_CONFIG_ERROR_CODES


class MockSzError(Exception):
    """Mock Senzing error."""
    pass


class MockSzNotFoundError(Exception):
    """Mock Senzing not found error."""
    pass


@pytest.fixture
def mock_senzing():
    """Set up mocked Senzing SDK."""
    with patch.dict('sys.modules', {
        'senzing': MagicMock(),
        'senzing_core': MagicMock()
    }):
        # Patch the error classes
        with patch('senzing_mcp.sdk_wrapper.SzError', MockSzError):
            with patch('senzing_mcp.sdk_wrapper.SzNotFoundError', MockSzNotFoundError):
                yield


@pytest.fixture
def wrapper():
    """Create a wrapper instance with mocked internals."""
    w = SenzingSDKWrapper()
    w._initialized = True
    w.engine = MagicMock()
    w.factory = MagicMock()
    return w


class TestStaleConfigDetection:
    """Test detection of stale config errors."""

    def test_detects_senz2062(self, wrapper):
        """Should detect SENZ2062 as stale config error."""
        error = Exception("SENZ2062|Requested lookup of [DSRC_ID] using unknown value [1001]")
        assert wrapper._is_stale_config_error(error) is True

    def test_detects_senz0033(self, wrapper):
        """Should detect SENZ0033 as stale config error."""
        error = Exception("SENZ0033|Some other stale config message")
        assert wrapper._is_stale_config_error(error) is True

    def test_ignores_other_errors(self, wrapper):
        """Should not flag non-stale errors for reinit."""
        error = Exception("SENZ1234|Some other error")
        assert wrapper._is_stale_config_error(error) is False

    def test_ignores_generic_errors(self, wrapper):
        """Should not flag generic errors for reinit."""
        error = Exception("Connection failed")
        assert wrapper._is_stale_config_error(error) is False


class TestAutoReinit:
    """Test automatic reinitialization on stale config errors."""

    @pytest.mark.asyncio
    async def test_reinit_on_stale_config_get_entity(self, wrapper):
        """Should reinitialize and retry on SENZ2062 for get_entity."""
        call_count = 0

        def mock_get_entity(entity_id, flags):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise MockSzError("SENZ2062|Requested lookup of [DSRC_ID] using unknown value [1001]")
            return '{"RESOLVED_ENTITY": {"ENTITY_ID": 1}}'

        wrapper.engine.get_entity_by_entity_id = mock_get_entity

        # Mock reinitialize
        reinit_called = False
        async def mock_reinit():
            nonlocal reinit_called
            reinit_called = True
        wrapper.reinitialize = mock_reinit

        # Patch SzError for the except block
        with patch('senzing_mcp.sdk_wrapper.SzError', MockSzError):
            with patch('senzing_mcp.sdk_wrapper.SzNotFoundError', MockSzNotFoundError):
                result = await wrapper.get_entity_by_entity_id(1)

        assert reinit_called, "reinitialize() should have been called"
        assert call_count == 2, "SDK should have been called twice (initial + retry)"
        assert "RESOLVED_ENTITY" in result

    @pytest.mark.asyncio
    async def test_no_reinit_on_regular_error(self, wrapper):
        """Should NOT reinitialize on non-stale errors."""
        def mock_get_entity(entity_id, flags):
            raise MockSzError("SENZ9999|Some other error")

        wrapper.engine.get_entity_by_entity_id = mock_get_entity

        reinit_called = False
        async def mock_reinit():
            nonlocal reinit_called
            reinit_called = True
        wrapper.reinitialize = mock_reinit

        with patch('senzing_mcp.sdk_wrapper.SzError', MockSzError):
            with patch('senzing_mcp.sdk_wrapper.SzNotFoundError', MockSzNotFoundError):
                result = await wrapper.get_entity_by_entity_id(1)

        assert not reinit_called, "reinitialize() should NOT have been called"
        result_data = json.loads(result)
        assert "error" in result_data

    @pytest.mark.asyncio
    async def test_reinit_only_once(self, wrapper):
        """Should only retry once, not infinitely loop."""
        call_count = 0

        def mock_get_entity(entity_id, flags):
            nonlocal call_count
            call_count += 1
            # Always throw stale config error
            raise MockSzError("SENZ2062|Stale config")

        wrapper.engine.get_entity_by_entity_id = mock_get_entity

        reinit_count = 0
        async def mock_reinit():
            nonlocal reinit_count
            reinit_count += 1
        wrapper.reinitialize = mock_reinit

        with patch('senzing_mcp.sdk_wrapper.SzError', MockSzError):
            with patch('senzing_mcp.sdk_wrapper.SzNotFoundError', MockSzNotFoundError):
                result = await wrapper.get_entity_by_entity_id(1)

        assert reinit_count == 1, "reinitialize() should only be called once"
        assert call_count == 2, "SDK should be called exactly twice"
        result_data = json.loads(result)
        assert "error" in result_data

    @pytest.mark.asyncio
    async def test_reinit_on_stale_config_search(self, wrapper):
        """Should reinitialize and retry on SENZ2062 for search."""
        call_count = 0

        def mock_search(attrs, flags):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise MockSzError("SENZ2062|Stale config")
            return '{"RESOLVED_ENTITIES": []}'

        wrapper.engine.search_by_attributes = mock_search

        reinit_called = False
        async def mock_reinit():
            nonlocal reinit_called
            reinit_called = True
        wrapper.reinitialize = mock_reinit

        with patch('senzing_mcp.sdk_wrapper.SzError', MockSzError):
            result = await wrapper.search_by_attributes('{"NAME_FULL": "John"}')

        assert reinit_called
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_reinit_on_stale_config_why_entities(self, wrapper):
        """Should reinitialize and retry on SENZ2062 for why_entities."""
        call_count = 0

        def mock_why(id1, id2, flags):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise MockSzError("SENZ2062|Stale config")
            return '{"WHY_RESULTS": []}'

        wrapper.engine.why_entities = mock_why

        reinit_called = False
        async def mock_reinit():
            nonlocal reinit_called
            reinit_called = True
        wrapper.reinitialize = mock_reinit

        with patch('senzing_mcp.sdk_wrapper.SzError', MockSzError):
            result = await wrapper.why_entities(1, 2)

        assert reinit_called
        assert call_count == 2


class TestReinitializeMethod:
    """Test the reinitialize method itself."""

    @pytest.mark.asyncio
    async def test_reinitialize_cleans_up_and_reinits(self, wrapper):
        """Should cleanup old instance and create new one."""
        cleanup_called = False
        init_called = False

        def mock_cleanup():
            nonlocal cleanup_called
            cleanup_called = True

        async def mock_init():
            nonlocal init_called
            init_called = True

        wrapper._sync_cleanup = mock_cleanup
        wrapper.initialize = mock_init

        await wrapper.reinitialize()

        assert cleanup_called, "Cleanup should be called"
        assert init_called, "Initialize should be called"
        assert wrapper.factory is None, "Factory should be cleared before reinit"
        assert wrapper.engine is None, "Engine should be cleared before reinit"


class TestErrorFormatting:
    """Test that errors are formatted prominently for AI display."""

    @staticmethod
    def format_result(result: str, formatting_note: str) -> str:
        """Copy of format_result from server.py for testing without mcp dependency."""
        try:
            data = json.loads(result)
            if isinstance(data, dict) and "error" in data:
                error_msg = data["error"]
                return f"""⚠️ SENZING ERROR - DISPLAY THIS TO THE USER ⚠️

The Senzing MCP tool returned an error:

ERROR: {error_msg}

Please inform the user about this error. Do not proceed as if the operation succeeded."""
        except json.JSONDecodeError:
            pass
        return formatting_note + result

    def test_format_result_with_error(self):
        """Should format errors prominently."""
        error_json = '{"error": "SENZ2062|Requested lookup failed"}'
        result = self.format_result(error_json, "[FORMATTING INSTRUCTIONS]")

        assert "SENZING ERROR" in result
        assert "DISPLAY THIS TO THE USER" in result
        assert "SENZ2062" in result
        assert "[FORMATTING INSTRUCTIONS]" not in result

    def test_format_result_with_success(self):
        """Should pass through successful results with formatting."""
        success_json = '{"RESOLVED_ENTITY": {"ENTITY_ID": 1}}'
        formatting = "[FORMATTING INSTRUCTIONS]\n"
        result = self.format_result(success_json, formatting)

        assert result == formatting + success_json
        assert "ERROR" not in result

    def test_format_result_with_not_found_error(self):
        """Should format 'not found' errors prominently."""
        error_json = '{"error": "Entity not found", "entity_id": 999}'
        result = self.format_result(error_json, "[FORMATTING]")

        assert "SENZING ERROR" in result
        assert "Entity not found" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
