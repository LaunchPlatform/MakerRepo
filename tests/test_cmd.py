import pathlib

from click.testing import CliRunner

from mr.cmds.main import cli


def test_view(cli_runner: CliRunner, fixtures_folder: pathlib.Path):
    result = cli_runner.invoke(
        cli, ["artifacts", "view", str(fixtures_folder / "example.py")]
    )
    assert result.exit_code == 0
