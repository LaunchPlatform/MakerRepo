import importlib.util
import logging
import os.path
import pathlib
from types import ModuleType

import click

from ...artifacts.registry import collect
from ...artifacts.registry import Registry
from ..environment import Environment
from ..environment import pass_env
from .cli import cli

logger = logging.getLogger(__name__)


def load_module(module_spec: str) -> ModuleType:
    if module_spec.lower().endswith(".py") and os.path.exists(module_spec):
        module_path = pathlib.Path(module_spec)
        module_name = module_path.stem
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Could not load spec for module '{module_name}' at: {module_path}"
            )

        module_obj = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_obj)
        return module_obj
    return importlib.import_module(module_spec)


def collect_artifacts(module_spec: str) -> Registry:
    registry = collect([load_module(module_spec)])
    if not registry.artifacts:
        logger.error("No artifacts found")
    return registry


@cli.command(help="View artifact")
@click.argument("MODULE")
@click.argument("ARTIFACTS", nargs=-1)
@pass_env
def view(env: Environment, module: str, artifacts: tuple[str, ...]):
    registry = collect_artifacts(module)
    if not artifacts:
        target_artifacts = list(list(registry.artifacts)[0])[0]
        logger.info(
            "No artifacts provided, use the first one %s/%s",
            target_artifacts.module,
            target_artifacts.name,
        )


@cli.command(help="Export artifact")
@click.argument("MODULE")
@pass_env
def export(env: Environment, module: str):
    registry = collect_artifacts(module)
    # TODO:
