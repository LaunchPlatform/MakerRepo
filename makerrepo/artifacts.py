import dataclasses
import typing

import venusian

from . import constants


@dataclasses.dataclass(frozen=True)
class Artifact:
    module: str
    name: str
    func: typing.Callable
    sample: bool


def artifact(
    func: typing.Callable | None = None, sample: bool = False
) -> typing.Callable:
    def decorator(wrapped: typing.Callable):
        artifact_obj = Artifact(
            module=wrapped.__module__,
            name=wrapped.__name__,
            func=wrapped,
            sample=sample,
        )

        def callback(scanner: venusian.Scanner, name: str, ob: typing.Callable):
            if artifact_obj.name != name:
                raise ValueError("Name is not the same")
            scanner.registry.add(artifact_obj)

        venusian.attach(wrapped, callback, category=constants.MR_ARTIFACTS_CATEGORY)
        return wrapped

    if func is not None:
        return decorator(func)

    return decorator
