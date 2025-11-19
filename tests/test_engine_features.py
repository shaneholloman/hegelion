"""Tests for core engine functionality including personas and iterations."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hegelion.engine import HegelionEngine
from hegelion.models import HegelionResult
from hegelion.personas import SECURITY_ENGINEER, LOGICIAN, EMPIRICIST, get_personas


@pytest.mark.asyncio
class TestEngineFeatures:

    @pytest.fixture
    def mock_backend(self):
        backend = MagicMock()
        backend.generate = AsyncMock(return_value="Mocked Response")
        return backend

    async def test_iteration_logic(self, mock_backend):
        """Test that iterations run multiple times."""
        engine = HegelionEngine(backend=mock_backend, model="test-model")

        # Mock internal generation methods to track calls
        with (
            patch.object(engine, "_generate_thesis_phase", new_callable=AsyncMock) as mock_thesis,
            patch.object(engine, "_run_cycle", new_callable=AsyncMock) as mock_cycle,
        ):

            mock_thesis.return_value = "Initial Thesis"
            mock_cycle.return_value = HegelionResult(
                query="q",
                mode="synthesis",
                thesis="t",
                antithesis="a",
                synthesis="New Synthesis",
                contradictions=[],
                research_proposals=[],
                metadata={
                    "thesis_time_ms": 0,
                    "antithesis_time_ms": 0,
                    "synthesis_time_ms": 0,
                    "total_time_ms": 0,
                },
            )

            await engine.process_query("test query", max_iterations=3)

            assert mock_thesis.call_count == 1  # Thesis only generated once
            assert mock_cycle.call_count == 3  # Cycle runs 3 times

    async def test_multi_persona_logic(self, mock_backend):
        """Test that multiple personas trigger multiple calls."""
        engine = HegelionEngine(backend=mock_backend, model="test-model")

        personas = [LOGICIAN, EMPIRICIST]

        with (
            patch.object(
                engine, "_generate_persona_antithesis", new_callable=AsyncMock
            ) as mock_persona_gen,
            patch.object(engine, "_generate_antithesis", new_callable=AsyncMock) as mock_std_gen,
        ):

            # Mock returns
            mock_persona_gen.return_value = MagicMock(text="Critique", contradictions=[])

            # We need to mock the rest of the cycle to avoid crashes
            with patch.object(engine, "_generate_synthesis", new_callable=AsyncMock) as mock_synth:
                mock_synth.return_value = MagicMock(text="Synth", research_proposals=[])

                await engine._run_cycle(
                    "q",
                    "t",
                    personas=personas,
                    use_search=False,
                    debug=False,
                    start_time=0,
                    stream_callback=None,
                    progress_callback=None,
                )

                assert mock_persona_gen.call_count == 2  # Once per persona
                assert mock_std_gen.call_count == 0  # Standard antithesis skipped

    async def test_personas_resolution(self):
        """Test that personas string presets are resolved correctly."""
        # Test string preset
        personas = get_personas(preset_name="council")
        assert len(personas) == 3
        assert personas[0].name == "The Logician"
        assert personas[1].name == "The Empiricist"
        assert personas[2].name == "The Ethicist"

        # Test security preset
        personas = get_personas(preset_name="security")
        assert len(personas) == 1
        assert personas[0].name == "Security Engineer"

    async def test_search_instruction_injection(self, mock_backend):
        """Test that search instructions are injected into prompts."""
        engine = HegelionEngine(backend=mock_backend, model="test-model")

        with patch.object(engine, "_call_backend", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Response"

            # Test standard antithesis
            await engine._generate_antithesis("q", "t", use_search=True, stream_callback=None)
            args, _ = mock_call.call_args
            prompt = args[0]
            assert "available search tools" in prompt

            # Test persona antithesis
            await engine._generate_persona_antithesis(
                "q", "t", SECURITY_ENGINEER, use_search=True, stream_callback=None
            )
            args, _ = mock_call.call_args
            prompt = args[0]
            assert "available search tools" in prompt
