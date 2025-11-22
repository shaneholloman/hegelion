"""Simple file-based result caching for Hegelion."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .models import HegelionResult


@dataclass
class CacheConfig:
    """Configuration for result caching."""

    cache_dir: Path
    ttl_seconds: Optional[int] = None

    @classmethod
    def from_env(
        cls,
        cache_dir: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> "CacheConfig":
        resolved_dir = Path(cache_dir or os.path.expanduser("~/.cache/hegelion"))
        return cls(cache_dir=resolved_dir, ttl_seconds=ttl_seconds)


class ResultCache:
    """Tiny JSONL cache that stores complete HegelionResult payloads on disk."""

    def __init__(self, config: CacheConfig) -> None:
        self.config = config
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_key(self, key: str) -> Path:
        return self.config.cache_dir / f"{key}.json"

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load a cached result if it exists and is fresh."""
        path = self._path_for_key(key)
        if not path.exists():
            return None

        if self.config.ttl_seconds is not None:
            age = time.time() - path.stat().st_mtime
            if age > self.config.ttl_seconds:
                return None

        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return None

    def save(self, key: str, result: HegelionResult) -> None:
        """Persist a result atomically."""
        data = result.to_dict()
        path = self._path_for_key(key)
        tmp_path = path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        tmp_path.replace(path)


def compute_cache_key(
    query: str,
    model: str,
    backend_provider: str,
    *,
    version: str,
    max_tokens_per_phase: int,
    debug: bool,
) -> str:
    """Generate a stable cache key for a dialectic request."""
    canonical = json.dumps(
        {
            "query": query,
            "model": model,
            "backend": backend_provider,
            "max_tokens": max_tokens_per_phase,
            "debug": debug,
            "version": version,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
