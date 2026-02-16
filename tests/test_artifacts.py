import pathlib
import sys
import textwrap

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


@artifact(sample=True, short_desc="example")
def sample_artifact():
    """This is an example of doc

    - list0
    - list1
    """
    return "sample_artifact"


@artifact(desc="MOCK_DESC")
def artifact_with_desc():
    """This should be overridden by the doc arg"""
    return "artifact_with_desc"


@artifact(export_step=True)
def artifact_export_step():
    return "artifact_export_step"


@artifact(export_3mf=True)
def artifact_export_3mf():
    return "artifact_export_3mf"


@artifact(export_step=True, export_3mf=True)
def artifact_both_exports():
    return "artifact_both_exports"


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
                cover=False,
                filepath=artifact_without_params.__code__.co_filename,
                lineno=artifact_without_params.__code__.co_firstlineno,
            ),
            sample_artifact.__name__: Artifact(
                module=__name__,
                name=sample_artifact.__name__,
                func=sample_artifact,
                sample=True,
                cover=False,
                desc=textwrap.dedent("This is an example of doc\n\n- list0\n- list1"),
                short_desc="example",
                filepath=sample_artifact.__code__.co_filename,
                lineno=sample_artifact.__code__.co_firstlineno,
            ),
            artifact_with_desc.__name__: Artifact(
                module=__name__,
                name=artifact_with_desc.__name__,
                func=artifact_with_desc,
                sample=False,
                cover=False,
                desc="MOCK_DESC",
                filepath=artifact_with_desc.__code__.co_filename,
                lineno=artifact_with_desc.__code__.co_firstlineno,
            ),
            artifact_export_step.__name__: Artifact(
                module=__name__,
                name=artifact_export_step.__name__,
                func=artifact_export_step,
                sample=False,
                cover=False,
                filepath=artifact_export_step.__code__.co_filename,
                lineno=artifact_export_step.__code__.co_firstlineno,
                export_step=True,
                export_3mf=None,
            ),
            artifact_export_3mf.__name__: Artifact(
                module=__name__,
                name=artifact_export_3mf.__name__,
                func=artifact_export_3mf,
                sample=False,
                cover=False,
                filepath=artifact_export_3mf.__code__.co_filename,
                lineno=artifact_export_3mf.__code__.co_firstlineno,
                export_step=None,
                export_3mf=True,
            ),
            artifact_both_exports.__name__: Artifact(
                module=__name__,
                name=artifact_both_exports.__name__,
                func=artifact_both_exports,
                sample=False,
                cover=False,
                filepath=artifact_both_exports.__code__.co_filename,
                lineno=artifact_both_exports.__code__.co_firstlineno,
                export_step=True,
                export_3mf=True,
            ),
        }
    }
    assert artifact_without_params() == "artifact_without_params"
    assert sample_artifact() == "sample_artifact"


def test_artifact_export_step_and_export_3mf():
    """Ensure export_step and export_3mf are passed from decorator to Artifact."""
    module = sys.modules[__name__]
    registry = collect([module])
    artifacts = registry.artifacts[__name__]

    assert artifacts[artifact_export_step.__name__].export_step is True
    assert artifacts[artifact_export_step.__name__].export_3mf is None

    assert artifacts[artifact_export_3mf.__name__].export_step is None
    assert artifacts[artifact_export_3mf.__name__].export_3mf is True

    assert artifacts[artifact_both_exports.__name__].export_step is True
    assert artifacts[artifact_both_exports.__name__].export_3mf is True

    # Default (no kwargs) leaves both None
    assert artifacts[artifact_without_params.__name__].export_step is None
    assert artifacts[artifact_without_params.__name__].export_3mf is None


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
