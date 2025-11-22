"""
Hegelion Wrapper for Kimi CLI

This module provides a programmatic interface to the Kimi CLI tool,
allowing the training generator to leverage Kimi's reasoning capabilities
without direct API integration if needed, or as an alternative path.
"""

import asyncio
import json
import os
import subprocess
import sys
import re
import ast
from typing import Optional

class KimiCLIWrapper:
    """Wrapper around the 'kimi' command line tool."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self._check_installation()

    def _check_installation(self):
        """Verify kimi is installed and accessible."""
        try:
            subprocess.run(["kimi", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("kimi-cli is not installed. Run 'uv tool install kimi-cli'.")

    def _clean_output(self, raw_output: str) -> str:
        """
        Parses the raw verbose output from Kimi CLI (which contains Python object reprs)
        and extracts the actual text content.
        """
        # We prioritize extracting 'TextPart' as it typically contains the final coherent response.
        # Pattern matches text='...' inside TextPart, handling escaped quotes.
        text_pattern = re.compile(r"text='((?:[^'\\]|\\.)*)'", re.DOTALL)
        texts = text_pattern.findall(raw_output)
        
        decoded_texts = []
        for t in texts:
            try:
                # Wrap in quotes to create a valid python string literal, then decode
                decoded_texts.append(ast.literal_eval(f"'{t}'"))
            except Exception as e:
                # Fallback: simple unescape if eval fails
                print(f"Warning: Failed to decode text part via ast: {e}")
                decoded_texts.append(t.replace("\\n", "\n").replace("\\'", "'"))

        if decoded_texts:
            return "".join(decoded_texts).strip()

        # If no TextPart found, try finding 'ThinkPart' (partial/streaming thoughts)
        think_pattern = re.compile(r"think='((?:[^'\\]|\\.)*)'", re.DOTALL)
        thinks = think_pattern.findall(raw_output)
        
        decoded_thinks = []
        for t in thinks:
            try:
                decoded_thinks.append(ast.literal_eval(f"'{t}'"))
            except Exception:
                decoded_thinks.append(t.replace("\\n", "\n").replace("\\'", "'"))

        if decoded_thinks:
            return "".join(decoded_thinks).strip()

        # If neither structure is found, return raw output (it might be a clean string already?)
        return raw_output.strip()

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response using the Kimi CLI.
        """
        
        # Construct the full prompt including system instruction if possible
        # Kimi CLI might not have a flag for system prompt directly in one-shot mode
        # so we prepend it.
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser Query: {prompt}"

        # Use --print for non-interactive output and --query for the prompt
        cmd = ["kimi", "--print", "--query", full_prompt]
        
        # We need to ensure the environment has the API key if not configured globally
        env = os.environ.copy()
        if self.api_key:
            env["MOONSHOT_API_KEY"] = self.api_key

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode().strip()
            raise RuntimeError(f"Kimi CLI failed (code {proc.returncode}): {error_msg}")

        raw_output = stdout.decode().strip()
        return self._clean_output(raw_output)


# Singleton instance
_kimi_cli = None

def get_kimi_cli() -> KimiCLIWrapper:
    global _kimi_cli
    if _kimi_cli is None:
        _kimi_cli = KimiCLIWrapper()
    return _kimi_cli
