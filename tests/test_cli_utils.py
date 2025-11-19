"""Tests for CLI utility functions."""

from hegelion.scripts.hegelion_cli import parse_command_string


def test_parse_command_string_empty():
    cmd, args = parse_command_string("")
    assert cmd == ""
    assert args == []

    cmd, args = parse_command_string("   ")
    assert cmd == ""
    assert args == []


def test_parse_command_string_single_command():
    cmd, args = parse_command_string("help")
    assert cmd == "help"
    assert args == []

    cmd, args = parse_command_string("HELP")
    assert cmd == "help"
    assert args == []


def test_parse_command_string_command_with_args():
    cmd, args = parse_command_string("set model claude")
    assert cmd == "set"
    assert args == ["model", "claude"]

    cmd, args = parse_command_string("SHOW thesis")
    assert cmd == "show"
    assert args == ["thesis"]


def test_parse_command_string_extra_whitespace():
    cmd, args = parse_command_string("  set   debug   on  ")
    assert cmd == "set"
    assert args == ["debug", "on"]
