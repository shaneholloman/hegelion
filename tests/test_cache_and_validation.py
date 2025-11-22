"""Tests for caching and result validation layers."""

from pathlib import Path
from unittest.mock import patch

import pytest

from hegelion.core import run_dialectic
from hegelion.core.validation import ResultValidationError, validate_hegelion_result
from test_core import MockBackend, MockSettings


@pytest.mark.asyncio
async def test_run_dialectic_cache_hits(tmp_path: Path):
    backend = MockBackend()
    settings = MockSettings()
    settings.cache_enabled = True
    settings.cache_dir = str(tmp_path)
    settings.cache_ttl_seconds = 60

    with patch("hegelion.core.core.get_engine_settings", return_value=settings):
        first = await run_dialectic("Cache me", backend=backend, model="mock-model")
        first_calls = backend.call_count
        assert first_calls >= 3  # thesis, antithesis, synthesis (+conflict classifier)

        second = await run_dialectic("Cache me", backend=backend, model="mock-model")
        # A cache hit should not trigger new backend calls
        assert backend.call_count == first_calls
        assert first.to_dict() == second.to_dict()


def test_validate_hegelion_result_rejects_invalid_payload():
    from hegelion.core.models import HegelionResult

    bogus = HegelionResult(
        query="",
        mode="invalid",
        thesis="t",
        antithesis="a",
        synthesis="s",
        contradictions=[],
        research_proposals=[],
        metadata={
            "thesis_time_ms": 0.0,
            "antithesis_time_ms": 0.0,
            "synthesis_time_ms": 0.0,
            "total_time_ms": 0.0,
        },
    )
    bogus.metadata.pop("total_time_ms")

    with pytest.raises(ResultValidationError):
        validate_hegelion_result(bogus)
