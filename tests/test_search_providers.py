"""Tests for the search_providers module - Phase 2 search grounding."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import os

from hegelion.search_providers import (
    SearchProvider,
    TavilySearchProvider,
    DuckDuckGoSearchProvider,
    create_search_provider,
    search_for_context,
)


class TestSearchProviderABC:
    """Tests for the SearchProvider abstract base class."""

    def test_search_provider_is_abstract(self):
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            SearchProvider()

    def test_search_provider_subclass_must_implement_search(self):
        class IncompleteProvider(SearchProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()


class TestTavilySearchProvider:
    """Tests for the TavilySearchProvider class."""

    def test_tavily_provider_raises_without_package(self):
        with patch.dict("sys.modules", {"tavily": None}):
            with pytest.raises(RuntimeError) as exc_info:
                # This should raise because tavily package is mocked as not installed
                TavilySearchProvider(api_key="test-key")

            # The actual error message depends on import behavior
            # Just verify it raises a RuntimeError

    @pytest.mark.asyncio
    async def test_tavily_search_success(self):
        # Mock the tavily module
        mock_tavily_client = MagicMock()
        mock_tavily_client.search.return_value = {
            "answer": "This is the AI summary",
            "results": [
                {"content": "Result 1 content", "url": "https://example.com/1"},
                {"content": "Result 2 content", "url": "https://example.com/2"},
            ]
        }

        with patch.dict("sys.modules", {"tavily": MagicMock()}):
            with patch("hegelion.search_providers.TavilySearchProvider.__init__", return_value=None):
                provider = TavilySearchProvider.__new__(TavilySearchProvider)
                provider.client = mock_tavily_client
                provider.api_key = "test-key"

                results = await provider.search("test query", max_results=5)

                assert len(results) > 0
                assert "Summary:" in results[0]
                mock_tavily_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_tavily_search_handles_failure(self):
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("API error")

        with patch.dict("sys.modules", {"tavily": MagicMock()}):
            with patch("hegelion.search_providers.TavilySearchProvider.__init__", return_value=None):
                provider = TavilySearchProvider.__new__(TavilySearchProvider)
                provider.client = mock_client
                provider.api_key = "test-key"

                results = await provider.search("test query")

                assert results == []


class TestDuckDuckGoSearchProvider:
    """Tests for the DuckDuckGoSearchProvider class."""

    @pytest.mark.asyncio
    async def test_ddg_search_success(self):
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "body": "Body 1", "href": "https://example.com/1"},
            {"title": "Result 2", "body": "Body 2", "href": "https://example.com/2"},
        ]

        with patch.dict("sys.modules", {"duckduckgo_search": MagicMock()}):
            with patch("hegelion.search_providers.DuckDuckGoSearchProvider.__init__", return_value=None):
                provider = DuckDuckGoSearchProvider.__new__(DuckDuckGoSearchProvider)
                provider.ddgs = mock_ddgs

                results = await provider.search("test query", max_results=5)

                assert len(results) == 2
                assert "Title: Result 1" in results[0]
                assert "Body 1" in results[0]

    @pytest.mark.asyncio
    async def test_ddg_search_handles_failure(self):
        mock_ddgs = MagicMock()
        mock_ddgs.text.side_effect = Exception("Network error")

        with patch.dict("sys.modules", {"duckduckgo_search": MagicMock()}):
            with patch("hegelion.search_providers.DuckDuckGoSearchProvider.__init__", return_value=None):
                provider = DuckDuckGoSearchProvider.__new__(DuckDuckGoSearchProvider)
                provider.ddgs = mock_ddgs

                results = await provider.search("test query")

                assert results == []

    @pytest.mark.asyncio
    async def test_ddg_search_empty_results(self):
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = []

        with patch.dict("sys.modules", {"duckduckgo_search": MagicMock()}):
            with patch("hegelion.search_providers.DuckDuckGoSearchProvider.__init__", return_value=None):
                provider = DuckDuckGoSearchProvider.__new__(DuckDuckGoSearchProvider)
                provider.ddgs = mock_ddgs

                results = await provider.search("test query")

                assert results == []


class TestCreateSearchProvider:
    """Tests for the create_search_provider factory function."""

    def test_create_provider_prefers_tavily(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            with patch("hegelion.search_providers.TavilySearchProvider") as mock_tavily:
                mock_instance = MagicMock()
                mock_tavily.return_value = mock_instance

                result = create_search_provider()

                mock_tavily.assert_called_once_with("test-key")
                assert result == mock_instance

    def test_create_provider_falls_back_to_ddg(self):
        # No Tavily key
        with patch.dict(os.environ, {}, clear=True):
            # Remove TAVILY_API_KEY if present
            os.environ.pop("TAVILY_API_KEY", None)

            with patch("hegelion.search_providers.DuckDuckGoSearchProvider") as mock_ddg:
                mock_instance = MagicMock()
                mock_ddg.return_value = mock_instance

                result = create_search_provider()

                mock_ddg.assert_called_once()
                assert result == mock_instance

    def test_create_provider_returns_none_when_all_fail(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("TAVILY_API_KEY", None)

            with patch("hegelion.search_providers.DuckDuckGoSearchProvider") as mock_ddg:
                mock_ddg.side_effect = RuntimeError("No package")

                result = create_search_provider()

                assert result is None

    def test_create_provider_handles_tavily_failure(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            with patch("hegelion.search_providers.TavilySearchProvider") as mock_tavily:
                mock_tavily.side_effect = RuntimeError("Tavily failed")

                with patch("hegelion.search_providers.DuckDuckGoSearchProvider") as mock_ddg:
                    mock_instance = MagicMock()
                    mock_ddg.return_value = mock_instance

                    result = create_search_provider()

                    # Should fall back to DDG
                    assert result == mock_instance


class TestSearchForContext:
    """Tests for the search_for_context convenience function."""

    @pytest.mark.asyncio
    async def test_search_for_context_success(self):
        mock_provider = MagicMock()
        mock_provider.search = AsyncMock(return_value=["Context 1", "Context 2"])

        with patch("hegelion.search_providers.create_search_provider") as mock_create:
            mock_create.return_value = mock_provider

            results = await search_for_context("test query", max_results=5)

            assert results == ["Context 1", "Context 2"]
            mock_provider.search.assert_called_once_with("test query", 5)

    @pytest.mark.asyncio
    async def test_search_for_context_no_provider(self):
        with patch("hegelion.search_providers.create_search_provider") as mock_create:
            mock_create.return_value = None

            results = await search_for_context("test query")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_for_context_default_max_results(self):
        mock_provider = MagicMock()
        mock_provider.search = AsyncMock(return_value=["Result"])

        with patch("hegelion.search_providers.create_search_provider") as mock_create:
            mock_create.return_value = mock_provider

            await search_for_context("test query")

            # Should use default max_results=5
            mock_provider.search.assert_called_once_with("test query", 5)
