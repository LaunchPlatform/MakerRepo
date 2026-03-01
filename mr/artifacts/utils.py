import dataclasses
import importlib
import os
import pathlib
import sys
from importlib.machinery import SourceFileLoader
from types import ModuleType

import yaml

from ..constants import REPO_CONFIG_PATH
from .data_types import Artifact
from .data_types import DefaultArtifactConfig
from .data_types import RepoConfig


def load_module(module_spec: str) -> ModuleType:
    if module_spec.lower().endswith(".py") and os.path.exists(module_spec):
        module_path = pathlib.Path(module_spec)
        module_name = module_path.stem
        return SourceFileLoader(module_name, str(module_path)).load_module(module_name)
    try:
        current_dir = str(pathlib.Path.cwd())
        sys.path.insert(0, current_dir)
        return importlib.import_module(module_spec)
    finally:
        del sys.path[0]


def find_python_packages(path: pathlib.Path) -> list[str]:
    """
    Find top-level Python packages (directories with __init__.py) in the given path,
    excluding dot-prefixed dirs (e.g. .venv), and common test package names.
    """
    packages = []

    for item in path.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue
        if item.name.lower().startswith("test"):
            continue
        if not (item / "__init__.py").exists():
            continue
        packages.append(item.name)

    return packages


def find_python_modules(path: pathlib.Path) -> list[pathlib.Path]:
    """
    Find top-level Python modules (.py files) in the given path,
    excluding common test module names and setup files.
    """
    ignored_names = {
        "setup.py",
        "conftest.py",
    }

    modules = []

    for file in path.glob("*.py"):
        if not file.is_file():
            continue
        stem = file.stem
        if stem == "__init__":
            continue
        if stem.lower() in ignored_names:
            continue
        if stem.lower().startswith("test"):
            continue
        modules.append(file)

    return modules


def load_repo_config(path: str | pathlib.Path | None = None) -> RepoConfig:
    """
    Load repo config from a YAML file. Uses REPO_CONFIG_PATH by default if path is not given.
    If the file is missing, returns a default RepoConfig.
    """
    config_path = pathlib.Path(path if path is not None else REPO_CONFIG_PATH)
    if not config_path.exists():
        return RepoConfig()
    data = yaml.safe_load(config_path.read_text())
    if data is None:
        return RepoConfig()
    return RepoConfig.model_validate(data)


def apply_repo_config(artifact: Artifact, config: RepoConfig) -> Artifact:
    """
    Apply repo config defaults to an artifact. Like, if the artifact has None for
    export_step or export_3mf, fill in values from config.artifacts.default_config.
    """
    defaults = (
        config.artifacts.default_config
        if config.artifacts is not None
        else DefaultArtifactConfig()
    )
    kwargs: dict = {}
    if artifact.export_step is None:
        kwargs["export_step"] = defaults.export_step
    if artifact.export_3mf is None:
        kwargs["export_3mf"] = defaults.export_3mf
    if not kwargs:
        return artifact
    return dataclasses.replace(artifact, **kwargs)
