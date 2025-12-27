import importlib.util
import os.path
import pathlib

import click

from ...artifacts.registry import collect
from ..environment import Environment
from ..environment import pass_env
from .cli import cli


@cli.command(help="View artifact")
@click.argument("MODULE")
@pass_env
def view(env: Environment, module: str):
    if module.lower().endswith(".py") and os.path.exists(module):
        module_path = pathlib.Path(module)
        module_name = module_path.stem
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Could not load spec for module '{module_name}' at: {module_path}"
            )

        module_obj = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_obj)
    else:
        module_obj = importlib.import_module(module)
    registry = collect([module_obj])
