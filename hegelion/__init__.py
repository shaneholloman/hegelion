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
from .datasets import export_training_data, to_dpo_dataset, to_instruction_tuning_dataset
from .agent import HegelionAgent

__version__ = "0.3.0"
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
    "HegelionAgent",
    "to_dpo_dataset",
    "to_instruction_tuning_dataset",
    "export_training_data",
]
