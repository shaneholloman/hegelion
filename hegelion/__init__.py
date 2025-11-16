"""
Hegelion: Dialectical Reasoning Harness for LLMs

A Python package that generates structured thesis-antithesis-synthesis responses
using Large Language Models, making reasoning patterns and contradictions explicit.
"""

from .core import (
    run_dialectic,
    run_benchmark,
    run_dialectic_sync,
    run_benchmark_sync,
    dialectic,
    quickstart,
    dialectic_sync,
    quickstart_sync,
)
from .models import HegelionResult

__version__ = "0.2.2"
__author__ = "Hegelion Contributors"

__all__ = [
    "run_dialectic",
    "run_benchmark",
    "run_dialectic_sync",
    "run_benchmark_sync",
    "dialectic",
    "quickstart",
    "dialectic_sync",
    "quickstart_sync",
    "HegelionResult",
]
