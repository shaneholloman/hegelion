"""Search providers for grounding antithesis with real-world information."""

from __future__ import annotations

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger(__name__)


class SearchProvider(ABC):
    """Abstract base class for search providers."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[str]:
        """Search for context snippets related to the query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of context snippets
        """
        pass


class TavilySearchProvider(SearchProvider):
    """Tavily search provider - optimized for AI agents."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from tavily import TavilyClient

            self.client = TavilyClient(api_key=api_key)
        except ImportError:
            raise RuntimeError("tavily-python not installed. Run: pip install tavily-python")

    async def search(self, query: str, max_results: int = 5) -> List[str]:
        """Search using Tavily's agent-optimized API."""
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False,
            )

            snippets = []

            # Add the AI-generated answer if available
            if response.get("answer"):
                snippets.append(f"Summary: {response['answer']}")

            # Add search results
            for result in response.get("results", []):
                content = result.get("content", "").strip()
                url = result.get("url", "")
                if content:
                    snippet = f"Source: {url}\n{content}"
                    snippets.append(snippet)

            return snippets[:max_results]

        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
            return []


class DuckDuckGoSearchProvider(SearchProvider):
    """DuckDuckGo search provider - free, no API key required."""

    def __init__(self):
        try:
            from duckduckgo_search import DDGS

            self.ddgs = DDGS()
        except ImportError:
            raise RuntimeError(
                "duckduckgo-search not installed. Run: pip install duckduckgo-search"
            )

    async def search(self, query: str, max_results: int = 5) -> List[str]:
        """Search using DuckDuckGo's free API."""
        try:
            results = self.ddgs.text(keywords=query, max_results=max_results, safesearch="moderate")

            snippets = []
            for result in results:
                title = result.get("title", "")
                body = result.get("body", "")
                href = result.get("href", "")

                if body:
                    snippet = f"Title: {title}\nSource: {href}\n{body}"
                    snippets.append(snippet)

            return snippets

        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
            return []


def create_search_provider() -> Optional[SearchProvider]:
    """Factory function to create the best available search provider.

    Returns:
        SearchProvider instance, or None if no providers available
    """
    # Try Tavily first (premium, agent-optimized)
    tavily_key = os.environ.get("TAVILY_API_KEY")
    if tavily_key:
        try:
            logger.info("Using Tavily search provider (premium)")
            return TavilySearchProvider(tavily_key)
        except RuntimeError as e:
            logger.warning(f"Tavily provider failed: {e}")

    # Fall back to DuckDuckGo (free)
    try:
        logger.info("Using DuckDuckGo search provider (free)")
        return DuckDuckGoSearchProvider()
    except RuntimeError as e:
        logger.warning(f"DuckDuckGo provider failed: {e}")

    logger.error(
        "No search providers available. Install: pip install duckduckgo-search tavily-python"
    )
    return None


async def search_for_context(query: str, max_results: int = 5) -> List[str]:
    """Search for context snippets to ground the antithesis.

    Args:
        query: Search query
        max_results: Maximum results to return

    Returns:
        List of context snippets, empty list if search fails
    """
    provider = create_search_provider()
    if not provider:
        return []

    return await provider.search(query, max_results)
