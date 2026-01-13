import pathlib
import sys

import pytest
from pytest import MonkeyPatch

from mr import Artifact
from mr import artifact
from mr.artifacts.registry import collect
from mr.artifacts.utils import find_python_modules
from mr.artifacts.utils import find_python_packages
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
                filepath=artifact_without_params.__code__.co_filename,
                lineno=artifact_without_params.__code__.co_firstlineno,
            ),
            sample_artifact.__name__: Artifact(
                module=__name__,
                name=sample_artifact.__name__,
                func=sample_artifact,
                sample=True,
                filepath=sample_artifact.__code__.co_filename,
                lineno=sample_artifact.__code__.co_firstlineno,
            ),
        }
    }
    assert artifact_without_params() == "artifact_without_params"
    assert sample_artifact() == "sample_artifact"


@pytest.mark.parametrize(
    "subdir,expected_packages",
    [
        ("examples", []),
        ("pkg_example", ["mypkg"]),
    ],
)
def test_find_python_packages(
    fixtures_folder: pathlib.Path,
    subdir: str,
    expected_packages: list[str],
):
    path = fixtures_folder / subdir
    packages = find_python_packages(path)
    assert set(packages) == set(expected_packages), (
        f"Expected packages {expected_packages} but got {packages} in {subdir}"
    )


@pytest.mark.parametrize(
    "subdir,expected_modules",
    [
        ("examples", ["main"]),
        ("pkg_example", []),
    ],
)
def test_find_python_modules(
    fixtures_folder: pathlib.Path,
    subdir: str,
    expected_modules: list[str],
):
    path = fixtures_folder / subdir
    modules = find_python_modules(path)
    module_names = {m.stem for m in modules}
    assert set(module_names) == set(expected_modules), (
        f"Expected modules {expected_modules} but got {module_names} in {subdir}"
    )


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
