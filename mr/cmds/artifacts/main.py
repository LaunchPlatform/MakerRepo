import click

from ..environment import Environment
from ..environment import pass_env
from .cli import cli


@cli.command(help="View artifact")
@click.argument("MODULE")
@pass_env
def view(env: Environment, module: str):
    # TODO:
    pass
