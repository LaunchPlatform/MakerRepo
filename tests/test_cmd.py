import pathlib

import pytest
from click.testing import CliRunner
from pytest import MonkeyPatch

from .helper import switch_cwd
from mr.cmds.main import cli


@pytest.mark.parametrize(
    "module",
    [
        "examples/main.py",
        "examples.main",
    ],
)
def test_view(
    monkeypatch: MonkeyPatch,
    cli_runner: CliRunner,
    fixtures_folder: pathlib.Path,
    module: str,
):
    monkeypatch.syspath_prepend(fixtures_folder)

    with switch_cwd(fixtures_folder):
        result = cli_runner.invoke(
            cli,
            ["artifacts", "view", module],
            catch_exceptions=False,
        )
    assert result.exit_code == 0
    # TODO: run a local mock websocket server to see if the model is correctly sent
