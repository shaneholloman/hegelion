"""Tests for runtime configuration changes."""

from unittest.mock import patch

import pytest

from hegelion.core.config import get_config, set_config_value


def test_set_config_value_updates_config():
    """Test that set_config_value updates the configuration."""
    # Ensure we have a clean state
    get_config.cache_clear()
    config = get_config()
    original_model = config.model

    try:
        # Change model
        set_config_value("model", "test-runtime-model")
        assert get_config().model == "test-runtime-model"

        # Change provider
        set_config_value("provider", "test-provider")
        assert get_config().provider == "test-provider"

    finally:
        # Restore original values (though cache_clear in other tests should handle this)
        set_config_value("model", original_model)
        # We don't know original provider easily without saving it, but cache_clear is better.
        get_config.cache_clear()


def test_set_config_value_clears_backend_cache():
    """Test that changing backend settings clears the backend cache."""
    get_config.cache_clear()

    with patch("hegelion.core.config.get_backend_from_env") as mock_backend_func:
        # Mock the cache_clear method on the function
        mock_backend_func.cache_clear = patch(
            "hegelion.core.config.get_backend_from_env.cache_clear"
        ).start()

        try:
            set_config_value("model", "new-model")
            mock_backend_func.cache_clear.assert_called()

            mock_backend_func.cache_clear.reset_mock()

            set_config_value("synthesis_threshold", 0.9)
            # Should NOT call cache_clear for non-backend settings
            mock_backend_func.cache_clear.assert_not_called()

        finally:
            patch.stopall()
            get_config.cache_clear()


def test_set_config_value_invalid_key():
    """Test that setting an invalid key raises AttributeError."""
    get_config.cache_clear()

    with pytest.raises(AttributeError) as exc:
        set_config_value("non_existent_key", "value")

    assert "has no attribute 'non_existent_key'" in str(exc.value)
