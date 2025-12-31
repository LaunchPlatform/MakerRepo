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


def find_python_modules(path: pathlib.Path) -> list[pathlib.Path]:
    """
    Find top-level Python packages (directories with __init__.py) and modules (.py files)
    in the given path, excluding common test package names and setup files.
    """
    # Common test package/module names to exclude
    test_names = {
        "test",
        "tests",
        "_test",
        "_tests",
        "pytest",
        "unittest",
        "testing",
        "conftest",
        "setup",
        "setup.py",
    }

    modules = []

    # Find Python packages (directories with __init__.py)
    for item in path.iterdir():
        if item.is_dir():
            # Check if it's a Python package (has __init__.py)
            init_file = item / "__init__.py"
            if init_file.exists():
                # Exclude test-related directories
                if item.name not in test_names and not item.name.startswith("test_"):
                    modules.append(item)

    # Find Python modules (.py files)
    for file in path.glob("*.py"):
        if file.is_file():
            stem = file.stem
            # Exclude __init__, test files, and setup files
            if (
                stem != "__init__"
                and stem not in test_names
                and not stem.startswith("test_")
                and not stem.endswith("_test")
            ):
                modules.append(file)

    return modules
