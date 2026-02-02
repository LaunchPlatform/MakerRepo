import pathlib

import pytest


@pytest.fixture
def fixtures_folder() -> pathlib.Path:
    return pathlib.Path(__file__).parent / "fixtures"
