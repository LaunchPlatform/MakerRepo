from ..aliase import AliasedGroup
from ..cli import cli as root_cli


@root_cli.group(
    name="artifacts",
    help="Operations for artifacts.",
    cls=AliasedGroup,
)
def cli():
    pass
