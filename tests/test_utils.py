import pathlib

import pytest

from mr import Artifact
from mr.artifacts.data_types import ArtifactsConfig
from mr.artifacts.data_types import DefaultArtifactConfig
from mr.artifacts.data_types import RepoConfig
from mr.artifacts.utils import apply_repo_config
from mr.artifacts.utils import load_repo_config


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
artifacts:
  default_config:
    export_step: false
    export_3mf: true
"""
    )
    config = load_repo_config(config_file)
    assert config.artifacts is not None
    assert config.artifacts.default_config.export_step is False
    assert config.artifacts.default_config.export_3mf is True


def test_load_repo_config_empty_yaml_returns_default(tmp_path: pathlib.Path):
    """Empty or comment-only YAML yields default RepoConfig."""
    config_file = tmp_path / "empty.yaml"
    config_file.write_text("")
    config = load_repo_config(config_file)
    assert config.artifacts is None


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
