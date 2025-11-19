"""Comprehensive tests for caching functionality."""

import time
from pathlib import Path


from hegelion.cache import CacheConfig, ResultCache, compute_cache_key
from hegelion.models import HegelionResult


class TestCacheKeyComputation:
    """Tests for cache key computation."""

    def test_cache_key_deterministic(self):
        """Test that cache key is deterministic for same inputs."""
        key1 = compute_cache_key(
            query="Test query",
            model="test-model",
            backend_provider="TestBackend",
            version="1.0.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        key2 = compute_cache_key(
            query="Test query",
            model="test-model",
            backend_provider="TestBackend",
            version="1.0.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        assert key1 == key2

    def test_cache_key_different_for_different_queries(self):
        """Test that different queries produce different keys."""
        key1 = compute_cache_key(
            query="Query 1",
            model="test-model",
            backend_provider="TestBackend",
            version="1.0.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        key2 = compute_cache_key(
            query="Query 2",
            model="test-model",
            backend_provider="TestBackend",
            version="1.0.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        assert key1 != key2

    def test_cache_key_includes_all_parameters(self):
        """Test that all parameters affect the cache key."""
        base_key = compute_cache_key(
            query="Test",
            model="model",
            backend_provider="Backend",
            version="1.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        # Different model
        key2 = compute_cache_key(
            query="Test",
            model="different-model",
            backend_provider="Backend",
            version="1.0",
            max_tokens_per_phase=1000,
            debug=False,
        )
        assert base_key != key2

        # Different backend
        key3 = compute_cache_key(
            query="Test",
            model="model",
            backend_provider="DifferentBackend",
            version="1.0",
            max_tokens_per_phase=1000,
            debug=False,
        )
        assert base_key != key3

        # Different version
        key4 = compute_cache_key(
            query="Test",
            model="model",
            backend_provider="Backend",
            version="2.0",
            max_tokens_per_phase=1000,
            debug=False,
        )
        assert base_key != key4

        # Different max_tokens
        key5 = compute_cache_key(
            query="Test",
            model="model",
            backend_provider="Backend",
            version="1.0",
            max_tokens_per_phase=2000,
            debug=False,
        )
        assert base_key != key5

        # Different debug flag
        key6 = compute_cache_key(
            query="Test",
            model="model",
            backend_provider="Backend",
            version="1.0",
            max_tokens_per_phase=1000,
            debug=True,
        )
        assert base_key != key6

    def test_cache_key_length(self):
        """Test that cache key has reasonable length."""
        key = compute_cache_key(
            query="Test query",
            model="test-model",
            backend_provider="TestBackend",
            version="1.0.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        assert len(key) == 24  # SHA256 hex digest truncated to 24 chars

    def test_cache_key_unicode_safe(self):
        """Test that cache key handles unicode queries."""
        key = compute_cache_key(
            query="Test query with émojis 🚀 and 中文",
            model="test-model",
            backend_provider="TestBackend",
            version="1.0.0",
            max_tokens_per_phase=1000,
            debug=False,
        )

        assert len(key) == 24
        assert isinstance(key, str)


class TestCacheConfig:
    """Tests for CacheConfig."""

    def test_from_env_defaults(self):
        """Test CacheConfig.from_env with defaults."""
        config = CacheConfig.from_env()

        assert config.cache_dir == Path.home() / ".cache" / "hegelion"
        assert config.ttl_seconds is None

    def test_from_env_custom_dir(self):
        """Test CacheConfig.from_env with custom directory."""
        config = CacheConfig.from_env(cache_dir="/custom/path")

        assert config.cache_dir == Path("/custom/path")

    def test_from_env_custom_ttl(self):
        """Test CacheConfig.from_env with custom TTL."""
        config = CacheConfig.from_env(ttl_seconds=3600)

        assert config.ttl_seconds == 3600


class TestResultCache:
    """Tests for ResultCache."""

    def test_cache_directory_creation(self, tmp_path):
        """Test that cache directory is created automatically."""
        cache_dir = tmp_path / "cache"
        config = CacheConfig(cache_dir=cache_dir, ttl_seconds=None)

        _ = ResultCache(config)

        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_save_and_load(self, tmp_path):
        """Test saving and loading a result."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        result = HegelionResult(
            query="Test query",
            mode="synthesis",
            thesis="Thesis text",
            antithesis="Antithesis text",
            synthesis="Synthesis text",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 100.0,
                "antithesis_time_ms": 200.0,
                "synthesis_time_ms": 300.0,
                "total_time_ms": 600.0,
            },
        )

        cache_key = "test-key-123"
        cache.save(cache_key, result)

        loaded = cache.load(cache_key)

        assert loaded is not None
        assert loaded["query"] == "Test query"
        assert loaded["thesis"] == "Thesis text"
        assert loaded["mode"] == "synthesis"

    def test_load_nonexistent_key(self, tmp_path):
        """Test loading a non-existent cache key."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        loaded = cache.load("nonexistent-key")

        assert loaded is None

    def test_ttl_expiration(self, tmp_path):
        """Test that TTL expiration works."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=1)
        cache = ResultCache(config)

        result = HegelionResult(
            query="Test",
            mode="synthesis",
            thesis="T",
            antithesis="A",
            synthesis="S",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 0.0,
                "antithesis_time_ms": 0.0,
                "synthesis_time_ms": 0.0,
                "total_time_ms": 0.0,
            },
        )

        cache_key = "test-key"
        cache.save(cache_key, result)

        # Should be available immediately
        assert cache.load(cache_key) is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.load(cache_key) is None

    def test_ttl_none_no_expiration(self, tmp_path):
        """Test that TTL=None means no expiration."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        result = HegelionResult(
            query="Test",
            mode="synthesis",
            thesis="T",
            antithesis="A",
            synthesis="S",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 0.0,
                "antithesis_time_ms": 0.0,
                "synthesis_time_ms": 0.0,
                "total_time_ms": 0.0,
            },
        )

        cache_key = "test-key"
        cache.save(cache_key, result)

        # Should still be available after delay
        time.sleep(0.1)
        assert cache.load(cache_key) is not None

    def test_atomic_write(self, tmp_path):
        """Test that writes are atomic (use tmp file)."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        result = HegelionResult(
            query="Test",
            mode="synthesis",
            thesis="T",
            antithesis="A",
            synthesis="S",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 0.0,
                "antithesis_time_ms": 0.0,
                "synthesis_time_ms": 0.0,
                "total_time_ms": 0.0,
            },
        )

        cache_key = "test-key"
        cache.save(cache_key, result)

        # Should not have .tmp file left behind
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0

        # Should have the actual cache file
        cache_file = tmp_path / f"{cache_key}.json"
        assert cache_file.exists()

    def test_load_corrupted_json(self, tmp_path):
        """Test handling of corrupted JSON files."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        # Create a corrupted JSON file
        cache_file = tmp_path / "corrupted-key.json"
        cache_file.write_text("not valid json{")

        # Should return None instead of raising
        loaded = cache.load("corrupted-key")
        assert loaded is None

    def test_save_complex_result(self, tmp_path):
        """Test saving a complex result with all fields."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        result = HegelionResult(
            query="Complex query",
            mode="synthesis",
            thesis="Thesis with unicode: émojis 🚀",
            antithesis="Antithesis",
            synthesis="Synthesis",
            contradictions=[
                {"description": "Contradiction 1", "evidence": "Evidence 1"},
                {"description": "Contradiction 2"},
            ],
            research_proposals=[
                {
                    "description": "Proposal 1",
                    "testable_prediction": "Prediction 1",
                },
                {"description": "Proposal 2"},
            ],
            metadata={
                "thesis_time_ms": 123.45,
                "antithesis_time_ms": 234.56,
                "synthesis_time_ms": 345.67,
                "total_time_ms": 703.68,
                "backend_provider": "TestBackend",
                "backend_model": "test-model",
                "debug": {"internal_conflict_score": 0.85},
            },
            trace={
                "thesis": "Full thesis",
                "antithesis": "Full antithesis",
                "synthesis": "Full synthesis",
                "contradictions_found": 2,
                "research_proposals": ["Proposal 1", "Proposal 2"],
            },
        )

        cache_key = "complex-key"
        cache.save(cache_key, result)

        loaded = cache.load(cache_key)

        assert loaded is not None
        assert loaded["query"] == "Complex query"
        assert len(loaded["contradictions"]) == 2
        assert len(loaded["research_proposals"]) == 2
        assert "debug" in loaded["metadata"]
        assert "trace" in loaded

    def test_save_empty_result(self, tmp_path):
        """Test saving an empty/minimal result."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        result = HegelionResult(
            query="",
            mode="synthesis",
            thesis="",
            antithesis="",
            synthesis="",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 0.0,
                "antithesis_time_ms": 0.0,
                "synthesis_time_ms": 0.0,
                "total_time_ms": 0.0,
            },
        )

        cache_key = "empty-key"
        cache.save(cache_key, result)

        loaded = cache.load(cache_key)

        assert loaded is not None
        assert loaded["query"] == ""
        assert loaded["thesis"] == ""

    def test_multiple_keys(self, tmp_path):
        """Test caching multiple different keys."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        results = []
        for i in range(5):
            result = HegelionResult(
                query=f"Query {i}",
                mode="synthesis",
                thesis=f"Thesis {i}",
                antithesis=f"Antithesis {i}",
                synthesis=f"Synthesis {i}",
                contradictions=[],
                research_proposals=[],
                metadata={
                    "thesis_time_ms": float(i),
                    "antithesis_time_ms": float(i),
                    "synthesis_time_ms": float(i),
                    "total_time_ms": float(i * 3),
                },
            )
            cache.save(f"key-{i}", result)
            results.append(result)

        # All should be loadable
        for i in range(5):
            loaded = cache.load(f"key-{i}")
            assert loaded is not None
            assert loaded["query"] == f"Query {i}"

    def test_overwrite_existing_key(self, tmp_path):
        """Test overwriting an existing cache key."""
        config = CacheConfig(cache_dir=tmp_path, ttl_seconds=None)
        cache = ResultCache(config)

        result1 = HegelionResult(
            query="Original",
            mode="synthesis",
            thesis="T1",
            antithesis="A1",
            synthesis="S1",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 0.0,
                "antithesis_time_ms": 0.0,
                "synthesis_time_ms": 0.0,
                "total_time_ms": 0.0,
            },
        )

        cache_key = "overwrite-key"
        cache.save(cache_key, result1)

        result2 = HegelionResult(
            query="Updated",
            mode="synthesis",
            thesis="T2",
            antithesis="A2",
            synthesis="S2",
            contradictions=[],
            research_proposals=[],
            metadata={
                "thesis_time_ms": 0.0,
                "antithesis_time_ms": 0.0,
                "synthesis_time_ms": 0.0,
                "total_time_ms": 0.0,
            },
        )

        cache.save(cache_key, result2)

        loaded = cache.load(cache_key)
        assert loaded["query"] == "Updated"
        assert loaded["thesis"] == "T2"
