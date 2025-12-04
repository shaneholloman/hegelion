
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from hegelion.mcp.server import call_tool
from hegelion.core.models import HegelionResult

@pytest.mark.asyncio
async def test_run_dialectic_tool():
    """Test the run_dialectic tool handler."""
    
    # Mock result
    mock_result = HegelionResult(
        thesis="Test thesis",
        antithesis="Test antithesis",
        synthesis="Test synthesis",
        research_proposals=["Proposal 1"],
        mode="test"
    )
    
    # Mock run_dialectic
    with patch("hegelion.core.core.run_dialectic", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_result
        
        # Call the tool
        contents, structured = await call_tool(
            "run_dialectic",
            {
                "query": "Test Query",
                "use_search": True
            }
        )
        
        # Verify run_dialectic was called with correct args
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["query"] == "Test Query"
        assert call_kwargs["use_search"] is True
        assert "progress_callback" in call_kwargs
        
        # Verify output structure
        assert len(contents) == 1
        assert "Test thesis" in contents[0].text
        assert "Test antithesis" in contents[0].text
        assert "Test synthesis" in contents[0].text
        assert "Proposal 1" in contents[0].text
        
        # Verify structured output
        assert structured["thesis"] == "Test thesis"

@pytest.mark.asyncio
async def test_run_dialectic_progress_callback():
    """Test that the progress callback bridge works."""
    
    # We need to capture the progress callback passed to run_dialectic
    captured_callback = None
    
    async def mock_run_dialectic(*args, **kwargs):
        nonlocal captured_callback
        captured_callback = kwargs.get("progress_callback")
        return HegelionResult(thesis="T", antithesis="A", synthesis="S", mode="test")

    # Mock _send_progress to verify it gets called
    with patch("hegelion.core.core.run_dialectic", side_effect=mock_run_dialectic):
        with patch("hegelion.mcp.server._send_progress", new_callable=AsyncMock) as mock_send_progress:
            # Set up request context mock if needed, but _send_progress handles missing context gracefully
            # For this test, we just want to see if it tries to call it.
            # However, _send_progress catches exceptions if context is missing.
            # To verify it's called, we need to ensure it doesn't just fail silently before the mock.
            # Actually, we can just patch it and see if the bridge calls it.
            
            await call_tool("run_dialectic", {"query": "Test"})
            
            # Now invoke the captured callback
            assert captured_callback is not None
            await captured_callback("phase_started", {"phase": "thesis"})
            
            # Verify _send_progress was called
            mock_send_progress.assert_called_with("━━━ Starting THESIS ━━━", 0.0)
