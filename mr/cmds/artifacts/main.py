import importlib
import logging
import os.path
import pathlib
import sys
from importlib.machinery import SourceFileLoader
from types import ModuleType

import click
import rich
from rich import box
from rich.markup import escape
from rich.padding import Padding
from rich.table import Table

from ...artifacts.registry import collect
from ...artifacts.registry import Registry
from ..environment import Environment
from ..environment import pass_env
from .cli import cli

logger = logging.getLogger(__name__)
TABLE_HEADER_STYLE = "yellow"
TABLE_COLUMN_STYLE = "cyan"


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


def collect_artifacts(module_spec: str) -> Registry:
    registry = collect([load_module(module_spec)])
    if not registry.artifacts:
        logger.error("No artifacts found")
    return registry


@cli.command(name="list", help="List artifacts")
@click.argument("MODULE")
@pass_env
def list_artifacts(env: Environment, module: str):
    registry = collect_artifacts(module)

    env.logger.info(
        "Listing artifacts for [blue]%s[/]",
        module,
        extra={"markup": True, "highlighter": None},
    )

    table = Table(
        title="Artifacts",
        box=box.SIMPLE,
        header_style=TABLE_HEADER_STYLE,
        expand=True,
    )
    table.add_column("Module", style=TABLE_COLUMN_STYLE)
    table.add_column("Name", style=TABLE_COLUMN_STYLE)
    table.add_column("Sample", style=TABLE_COLUMN_STYLE)
    for module, artifacts in registry.artifacts.items():
        for i, (name, artifact) in enumerate(artifacts.items()):
            table.add_row(
                escape(module) if i == 0 else "", escape(name), str(artifact.sample)
            )
    rich.print(Padding(table, (1, 0, 0, 4)))


@cli.command(help="View artifact")
@click.argument("MODULE")
@click.argument("ARTIFACTS", nargs=-1)
@click.option(
    "-p", "--port", help="OCP Viewer port to send the model data to", default=3939
)
@pass_env
def view(env: Environment, module: str, artifacts: tuple[str, ...], port: int):
    registry = collect_artifacts(module)
    if not artifacts:
        target_artifact = list(list(registry.artifacts.values())[0].values())[0]
        logger.info(
            "No artifacts provided, use the first one %s/%s",
            target_artifact.module,
            target_artifact.name,
        )
        target_artifacts = [target_artifact]
    else:
        if len(registry.artifacts) > 1:
            raise ValueError("Unexpected more than one modules found")
        module_artifacts = list(registry.artifacts.values())[0]
        target_artifacts = [
            module_artifacts[artifact_name] for artifact_name in artifacts
        ]

    # TODO: this is going to be a bit slow, provide a progress bar & cache?
    realized_artifacts = [artifact.func() for artifact in target_artifacts]
    # defer the import to make testing mocking much easier
    from ocp_vscode import show

    # TODO: pass in some args
    show(realized_artifacts, port=port)


@cli.command(help="Export artifact")
@click.argument("MODULE")
@pass_env
def export(env: Environment, module: str):
    registry = collect_artifacts(module)
    # TODO:
