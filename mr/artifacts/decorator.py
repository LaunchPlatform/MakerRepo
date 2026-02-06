import inspect
import typing

import venusian

from .. import constants
from .data_types import Artifact


def artifact(
    func: typing.Callable | None = None,
    *,
    sample: bool = False,
    cover: bool = False,
    desc: str | None = None,
    short_desc: str | None = None,
) -> typing.Callable:
    def decorator(wrapped: typing.Callable):
        nonlocal desc
        code = getattr(wrapped, "__code__", None)
        if desc is None:
            desc = inspect.getdoc(wrapped)
        artifact_obj = Artifact(
            module=wrapped.__module__,
            name=wrapped.__name__,
            func=wrapped,
            sample=sample,
            cover=cover,
            desc=desc,
            short_desc=short_desc,
            filepath=code.co_filename if code else None,
            lineno=code.co_firstlineno if code else None,
        )

        def callback(scanner: venusian.Scanner, name: str, ob: typing.Callable):
            if artifact_obj.name != name:
                raise ValueError("Name is not the same")
            scanner.registry.add(artifact_obj)

        venusian.attach(
            wrapped,
            callback,
            category=constants.MR_ARTIFACTS_CATEGORY,
            depth=1 if func is None else 2,
        )
        return wrapped

    if func is not None:
        return decorator(func)

    return decorator
