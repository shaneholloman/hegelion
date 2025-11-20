import json

import pytest

from hegelion.scripts import mcp_setup


def test_generate_config_includes_servers(tmp_path):
    cfg = mcp_setup.generate_config("/bin/python", tmp_path, is_installed=False)
    servers = cfg["mcpServers"]
    assert "hegelion" in servers and "hegelion-backend" in servers
    assert servers["hegelion"]["args"] == ["-m", "hegelion.prompt_mcp_server"]


def test_generate_config_sets_pythonpath_when_source(tmp_path):
    cfg = mcp_setup.generate_config("/bin/python", tmp_path, is_installed=False)
    env = cfg["mcpServers"]["hegelion"]["env"]
    assert env["PYTHONPATH"] == str(tmp_path)
    assert cfg["mcpServers"]["hegelion-backend"]["env"]["PYTHONPATH"] == str(tmp_path)


def test_generate_config_omits_env_when_installed(tmp_path):
    cfg = mcp_setup.generate_config("/bin/python", tmp_path, is_installed=True)
    assert "env" not in cfg["mcpServers"]["hegelion"]
    assert "env" not in cfg["mcpServers"]["hegelion-backend"]


def test_write_config_merges(tmp_path):
    target = tmp_path / "mcp.json"
    snippet = {"hegelion": {"command": "python", "args": ["-m", "h"]}}
    mcp_setup._write_config(target, snippet)
    payload = json.loads(target.read_text())
    assert payload["mcpServers"]["hegelion"]["command"] == "python"

    # Merge existing content
    snippet2 = {"other": {"command": "node", "args": ["srv"]}}
    mcp_setup._write_config(target, snippet2)
    payload = json.loads(target.read_text())
    assert set(payload["mcpServers"].keys()) == {"hegelion", "other"}


def test_is_installed_in_site_packages_detects_site(monkeypatch: pytest.MonkeyPatch, tmp_path):
    fake_site = tmp_path / "site-packages"
    fake_site.mkdir()
    fake_pkg = fake_site / "hegelion"
    fake_pkg.mkdir()
    fake_init = fake_pkg / "__init__.py"
    fake_init.write_text("", encoding="utf-8")

    monkeypatch.setattr(mcp_setup.site, "getsitepackages", lambda: [str(fake_site)])
    monkeypatch.setattr(mcp_setup.site, "getusersitepackages", lambda: str(fake_site))
    monkeypatch.setattr(mcp_setup.hegelion, "__file__", str(fake_init))

    assert mcp_setup.is_installed_in_site_packages() is True


def test_print_setup_instructions_mentions_py_path(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path):
    monkeypatch.setattr(mcp_setup, "get_python_path", lambda: "/bin/python")
    monkeypatch.setattr(mcp_setup, "is_installed_in_site_packages", lambda: False)
    monkeypatch.setattr(mcp_setup, "get_project_root", lambda: tmp_path)

    mcp_setup.print_setup_instructions()

    captured = capsys.readouterr()
    assert "hegelion-backend" in captured.out
    assert "Added PYTHONPATH" in captured.out
