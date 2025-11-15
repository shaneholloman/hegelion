"""
Hegelion: Dialectical Reasoning Harness for LLMs

A Python package that generates structured thesis-antithesis-synthesis responses
using Large Language Models, making reasoning patterns and contradictions explicit.
"""

from .core import run_dialectic, run_benchmark
from .models import HegelionResult

__version__ = "0.1.0"
__author__ = "Hegelion Contributors"

__all__ = [
    "run_dialectic",
    "run_benchmark",
    "HegelionResult",
]
