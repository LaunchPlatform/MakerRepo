import pathlib

from click.testing import CliRunner

from mr.cmds.main import cli


def test_view(cli_runner: CliRunner, fixtures_folder: pathlib.Path):
    result = cli_runner.invoke(
        cli,
        ["artifacts", "view", str(fixtures_folder / "example.py")],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    # TODO: run a local mock websocket server to see if the model is correctly sent
