import pathlib
import sys

import pytest
from pytest import MonkeyPatch

from mr import Artifact
from mr import artifact
from mr.artifacts.registry import collect
from mr.artifacts.utils import find_python_modules
from mr.artifacts.utils import load_module


@artifact
def artifact_without_params():
    return "artifact_without_params"


@artifact(sample=True)
def sample_artifact():
    return "sample_artifact"


def test_collect():
    module = sys.modules[__name__]
    registry = collect([module])
    assert registry.artifacts == {
        __name__: {
            artifact_without_params.__name__: Artifact(
                module=__name__,
                name=artifact_without_params.__name__,
                func=artifact_without_params,
                sample=False,
            ),
            sample_artifact.__name__: Artifact(
                module=__name__,
                name=sample_artifact.__name__,
                func=sample_artifact,
                sample=True,
            ),
        }
    }
    assert artifact_without_params() == "artifact_without_params"
    assert sample_artifact() == "sample_artifact"


@pytest.mark.parametrize(
    "subdir,expected_in,expected_not_in",
    [
        ("examples", ["main"], ["test_example", "tests", "__init__"]),
        ("pkg_example", ["mypkg"], []),
    ],
)
def test_find_python_modules(
    fixtures_folder: pathlib.Path,
    subdir: str,
    expected_in: list[str],
    expected_not_in: list[str],
):
    path = fixtures_folder / subdir
    modules = find_python_modules(path)
    module_names = {m.name if m.is_dir() else m.stem for m in modules}
    for name in expected_in:
        assert name in module_names, f"Expected {name} to be found in {subdir}"
    for name in expected_not_in:
        assert name not in module_names, f"Expected {name} not to be found in {subdir}"


@pytest.mark.parametrize(
    "module_spec,expected_name",
    [
        ("examples/main.py", "main"),
        ("examples.main", "examples.main"),
        ("pkg_example.mypkg.main", "pkg_example.mypkg.main"),
    ],
)
def test_load_module(
    fixtures_folder: pathlib.Path,
    monkeypatch: MonkeyPatch,
    module_spec: str,
    expected_name: str,
):
    if module_spec.endswith(".py"):
        # File path case
        module_path = fixtures_folder / module_spec
        module = load_module(str(module_path))
    else:
        # Module name case - requires sys.path setup
        monkeypatch.syspath_prepend(fixtures_folder)
        module = load_module(module_spec)

    assert module.__name__ == expected_name
    assert hasattr(module, "main")
