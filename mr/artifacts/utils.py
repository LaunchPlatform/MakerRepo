import importlib
import os
import pathlib
import sys
from importlib.machinery import SourceFileLoader
from types import ModuleType


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
    excluding common test package names.
    """
    packages = []

    for item in path.iterdir():
        if not item.is_dir():
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
