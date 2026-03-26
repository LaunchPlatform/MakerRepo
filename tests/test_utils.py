import pathlib

import pytest
from _pytest.monkeypatch import MonkeyPatch

from mr import Artifact
from mr.data_types import ArtifactsConfig
from mr.data_types import DefaultArtifactConfig
from mr.data_types import RepoConfig
from mr.utils import apply_pythonpaths
from mr.utils import apply_repo_config
from mr.utils import find_python_modules
from mr.utils import find_python_packages
from mr.utils import load_module
from mr.utils import load_repo_config


def test_load_repo_config_missing_file_returns_default(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """When default path does not exist, load_repo_config returns default RepoConfig."""
    monkeypatch.chdir(tmp_path)
    config = load_repo_config()
    assert config.artifacts is None


def test_load_repo_config_custom_path_missing_returns_default(tmp_path: pathlib.Path):
    """When custom path does not exist, load_repo_config returns default RepoConfig."""
    config = load_repo_config(tmp_path / "nonexistent.yaml")
    assert config.artifacts is None


def test_load_repo_config_custom_path_valid_yaml(tmp_path: pathlib.Path):
    """Load from a custom path with valid artifacts.default_config YAML."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
pythonpaths:
  - src
artifacts:
  default_config:
    export_step: false
    export_3mf: true
"""
    )
    config = load_repo_config(config_file)
    assert config.pythonpaths == ["src"]
    assert config.artifacts is not None
    assert config.artifacts.default_config.export_step is False
    assert config.artifacts.default_config.export_3mf is True


def test_load_repo_config_empty_yaml_returns_default(tmp_path: pathlib.Path):
    """Empty or comment-only YAML yields default RepoConfig."""
    config_file = tmp_path / "empty.yaml"
    config_file.write_text("")
    config = load_repo_config(config_file)
    assert config.pythonpaths == []
    assert config.artifacts is None


def test_apply_pythonpaths_prepends_to_sys_path(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    (tmp_path / "src").mkdir()
    config = RepoConfig(pythonpaths=["src"])
    monkeypatch.chdir(tmp_path)
    before = list(__import__("sys").path)
    with apply_pythonpaths(config) as added:
        assert added and added[0].endswith("/src")
        assert __import__("sys").path[0] == added[0]
        # Ensure we didn't blow away sys.path
        assert len(__import__("sys").path) >= len(before)
    assert __import__("sys").path == before


def test_apply_pythonpaths_resolves_relative_to_repo_root(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    repo_root = tmp_path / "repo"
    (repo_root / "src").mkdir(parents=True)
    config = RepoConfig(pythonpaths=["src"])
    monkeypatch.chdir(tmp_path)  # different cwd on purpose
    before = list(__import__("sys").path)
    with apply_pythonpaths(config, repo_root=repo_root) as added:
        assert added == [str((repo_root / "src").resolve())]
        assert __import__("sys").path[0] == added[0]
    assert __import__("sys").path == before


def test_apply_pythonpaths_does_not_remove_external_duplicate(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """
    If user code adds the same path again during the context, the context manager
    should only remove its own inserted occurrence and leave the external one.
    """
    sys = __import__("sys")
    (tmp_path / "src").mkdir()
    config = RepoConfig(pythonpaths=["src"])
    monkeypatch.chdir(tmp_path)

    before = list(sys.path)
    try:
        with apply_pythonpaths(config) as added:
            assert len(added) == 1
            value = added[0]
            assert sys.path[0] == value
            # Simulate other code adding the same path during the context.
            sys.path.append(value)
            assert sys.path.count(value) == 2
        # Our inserted occurrence is removed, but the "external" one remains.
        assert value in sys.path
        assert sys.path.count(value) == 1
    finally:
        # Restore sys.path so this test doesn't affect others.
        sys.path[:] = before


def test_apply_repo_config_fills_none_from_config():
    """apply_repo_config fills export_step/export_3mf when artifact has None."""

    def _dummy():
        pass

    artifact = Artifact(
        module="test",
        name="dummy",
        func=_dummy,
        sample=False,
        export_step=None,
        export_3mf=None,
    )
    config = RepoConfig(
        artifacts=ArtifactsConfig(
            default_config=DefaultArtifactConfig(export_step=False, export_3mf=True)
        )
    )
    resolved = apply_repo_config(artifact, config)
    assert resolved.export_step is False
    assert resolved.export_3mf is True


def test_apply_repo_config_leaves_explicit_values():
    """apply_repo_config does not override explicit export_step/export_3mf."""

    def _dummy():
        pass

    artifact = Artifact(
        module="test",
        name="dummy",
        func=_dummy,
        sample=False,
        export_step=True,
        export_3mf=False,
    )
    config = RepoConfig(
        artifacts=ArtifactsConfig(
            default_config=DefaultArtifactConfig(export_step=False, export_3mf=True)
        )
    )
    resolved = apply_repo_config(artifact, config)
    assert resolved.export_step is True
    assert resolved.export_3mf is False


def test_apply_repo_config_no_artifacts_section_uses_defaults():
    """When config.artifacts is None, DefaultArtifactConfig() defaults (True, True) are used."""

    def _dummy():
        pass

    artifact = Artifact(
        module="test",
        name="dummy",
        func=_dummy,
        sample=False,
        export_step=None,
        export_3mf=None,
    )
    config = RepoConfig()
    resolved = apply_repo_config(artifact, config)
    assert resolved.export_step is True
    assert resolved.export_3mf is True


def test_apply_repo_config_no_changes_returns_same_artifact():
    """When artifact has no Nones, the same artifact is returned."""

    def _dummy():
        pass

    artifact = Artifact(
        module="test",
        name="dummy",
        func=_dummy,
        sample=False,
        export_step=True,
        export_3mf=False,
    )
    config = RepoConfig()
    resolved = apply_repo_config(artifact, config)
    assert resolved is artifact


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
    "dir_names,expected_packages",
    [
        (["mypkg", ".venv", ".foo"], ["mypkg"]),
        (["mypkg", ".venv"], ["mypkg"]),
        ([".venv", ".foo"], []),
        (["mypkg"], ["mypkg"]),
    ],
)
def test_find_python_packages_ignores_dot_prefix(
    tmp_path: pathlib.Path,
    dir_names: list[str],
    expected_packages: list[str],
):
    """Dot-prefixed dirs (e.g. .venv) are ignored even if they have __init__.py."""
    for name in dir_names:
        (tmp_path / name).mkdir()
        (tmp_path / name / "__init__.py").touch()
    packages = find_python_packages(tmp_path)
    assert set(packages) == set(expected_packages)


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
