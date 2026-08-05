"""Tests for the evalmoraal command line interface."""

import pytest

from evalmoraal import __version__
from evalmoraal.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "run" in out
    assert "dashboard" in out


def test_run_help(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["run", "--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "--models" in out
    assert "--data-dir" in out
