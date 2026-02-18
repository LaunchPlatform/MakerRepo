import inspect
import typing

import venusian
from pydantic import BaseModel

from .. import constants
from .data_types import Artifact
from .data_types import Customizable


def artifact(
    func: typing.Callable | None = None,
    *,
    sample: bool = False,
    cover: bool = False,
    desc: str | None = None,
    short_desc: str | None = None,
    export_step: bool | None = None,
    export_3mf: bool | None = None,
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
            export_step=export_step,
            export_3mf=export_3mf,
        )

        def callback(scanner: venusian.Scanner, name: str, ob: typing.Callable):
            if artifact_obj.name != name:
                raise ValueError("Name is not the same")
            scanner.registry.add_artifact(artifact_obj)

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


def customizable(
    func: typing.Callable | None = None,
    *,
    desc: str | None = None,
    short_desc: str | None = None,
    sample_parameters: BaseModel | None = None,
) -> typing.Callable:
    def decorator(wrapped: typing.Callable):
        nonlocal desc
        code = getattr(wrapped, "__code__", None)
        if desc is None:
            desc = inspect.getdoc(wrapped)

        sig = inspect.signature(wrapped)
        if len(sig.parameters) != 1:
            raise ValueError(
                f"The customizable function should take exactly one argument, but we got {len(sig.parameters)} instead"
            )
        key = list(sig.parameters.keys())[0]
        parameters = sig.parameters[key]
        if not issubclass(parameters.annotation, BaseModel):
            raise ValueError(
                "The customizable function's parameter argument should be a subclass of pydantic.BaseModel, "
                f"but we got {parameters.annotation} instead"
            )

        customizable_obj = Customizable(
            module=wrapped.__module__,
            name=wrapped.__name__,
            func=wrapped,
            parameters=parameters.annotation,
            sample_parameters=sample_parameters,
            desc=desc,
            short_desc=short_desc,
            filepath=code.co_filename if code else None,
            lineno=code.co_firstlineno if code else None,
        )

        def callback(scanner: venusian.Scanner, name: str, ob: typing.Callable):
            if customizable_obj.name != name:
                raise ValueError("Name is not the same")
            scanner.registry.add_customizable(customizable_obj)

        venusian.attach(
            wrapped,
            callback,
            category=constants.MR_CUSTOMIZABLE_CATEGORY,
            depth=1 if func is None else 2,
        )
        return wrapped

    if func is not None:
        return decorator(func)

    return decorator
