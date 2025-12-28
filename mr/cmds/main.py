from .artifacts import main  # no qa
from .cli import cli

__ALL__ = [cli]

if __name__ == "__main__":
    cli()
