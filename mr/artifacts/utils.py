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
