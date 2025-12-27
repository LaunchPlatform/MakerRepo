import collections
import logging
import typing

import venusian

from .. import constants
from .data_types import Artifact


class Registry:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.artifacts = collections.defaultdict(dict)

    def add(self, artifact: Artifact):
        self.artifacts[artifact.module][artifact.name] = artifact


def collect(packages: list[typing.Any], registry: Registry | None = None) -> Registry:
    if registry is None:
        registry = Registry()
    scanner = venusian.Scanner(registry=registry)
    for package in packages:
        scanner.scan(package, categories=(constants.MR_ARTIFACTS_CATEGORY,))
    return registry
