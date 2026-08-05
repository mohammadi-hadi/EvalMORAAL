"""Tests for evalmoraal.env."""

import pytest

from evalmoraal.env import ENV_VARS, EnvLoader, get_env_loader


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ENV_VARS.values():
        monkeypatch.delenv(var, raising=False)


def test_get_api_key_from_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    loader = EnvLoader(env_file=tmp_path / "missing.env")

    assert loader.get_api_key("openai") == "sk-test"
    assert loader.has_key("openai")
    assert not loader.has_key("anthropic")
    assert loader.get_api_keys() == {"openai": "sk-test"}


def test_unknown_provider(tmp_path):
    loader = EnvLoader(env_file=tmp_path / "missing.env")
    assert loader.get_api_key("unknown") is None


def test_env_file_parsing(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment line\n"
        "\n"
        "OPENAI_API_KEY=file-key\n"
        "ANTHROPIC_API_KEY='quoted-key'\n"
        "not a key value line\n"
    )
    loader = EnvLoader(env_file=env_file)

    assert loader.get_api_key("openai") == "file-key"
    assert loader.get_api_key("anthropic") == "quoted-key"


def test_environment_wins_over_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=file-key\n")
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")

    loader = EnvLoader(env_file=env_file)
    assert loader.get_api_key("openai") == "env-key"


def test_environment_info(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
    loader = EnvLoader(env_file=tmp_path / "missing.env")

    info = loader.get_environment_info()
    assert info["has_anthropic"] is True
    assert info["has_openai"] is False
    assert info["configured_providers"] == ["anthropic"]


def test_available_models(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    loader = EnvLoader(env_file=tmp_path / "missing.env")

    models = loader.get_available_models()
    assert "api" in models
    assert any("gpt" in m for m in models["api"])


def test_get_env_loader_singleton(tmp_path):
    first = get_env_loader(env_file=tmp_path / "a.env")
    second = get_env_loader()
    assert second is first
