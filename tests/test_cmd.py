import pathlib

from click.testing import CliRunner

from mr.cmds.main import cli


def test_view(tmp_path: pathlib.Path, cli_runner: CliRunner):
    result = cli_runner.invoke(cli, ["artifacts", "view"])
