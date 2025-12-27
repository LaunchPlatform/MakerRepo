import pathlib

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def fixtures_folder() -> pathlib.Path:
    return pathlib.Path(__name__).parent / "fixtures"
