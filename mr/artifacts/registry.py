import collections
import logging
import typing

import venusian

from .. import constants
from .. import Customizable
from .data_types import Artifact


class Registry:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.artifacts: dict[str, dict[str, Artifact]] = collections.defaultdict(dict)
        self.customizables: dict[str, dict[str, Customizable]] = (
            collections.defaultdict(dict)
        )

    def add_artifact(self, artifact: Artifact):
        module_artifacts = self.artifacts[artifact.module]
        if artifact.name in module_artifacts:
            raise KeyError(
                f"artifact {artifact.name} already exists in {artifact.module}"
            )
        module_artifacts[artifact.name] = artifact

    def add_customizable(self, customizable: Customizable):
        module_customizables = self.customizables[customizable.module]
        if customizable.name in module_customizables:
            raise KeyError(
                f"customizable {customizable.name} already exists in {customizable.module}"
            )
        module_customizables[customizable.name] = customizable


def collect(
    packages: list[typing.Any],
    registry: Registry | None = None,
    onerror: typing.Callable[[str], None] | None = None,
) -> Registry:
    if registry is None:
        registry = Registry()
    scanner = venusian.Scanner(registry=registry)
    for package in packages:
        scanner.scan(
            package,
            categories=(
                constants.MR_ARTIFACTS_CATEGORY,
                constants.MR_CUSTOMIZABLE_CATEGORY,
            ),
            onerror=onerror,
        )
    return registry
