import sys
import textwrap

import pytest
from pydantic import BaseModel

from mr import Customizable
from mr import customizable
from mr.artifacts.registry import collect


class SizeParams(BaseModel):
    width: int
    height: int


@customizable(short_desc="example")
def customizable_artifact(params: SizeParams):
    """This is an example of doc

    - list0
    - list1
    """
    return "customizable_artifact"


@customizable(
    short_desc="example_with_sample_params",
    sample_parameters=SizeParams(width=123, height=456),
)
def customizable_with_sample_parameters(params: SizeParams):
    return "customizable_with_sample_parameters"


def test_collect():
    module = sys.modules[__name__]
    registry = collect([module])
    assert registry.customizables == {
        __name__: {
            customizable_artifact.__name__: Customizable(
                module=__name__,
                name=customizable_artifact.__name__,
                func=customizable_artifact,
                parameters=SizeParams,
                filepath=customizable_artifact.__code__.co_filename,
                lineno=customizable_artifact.__code__.co_firstlineno,
                desc=textwrap.dedent("This is an example of doc\n\n- list0\n- list1"),
                short_desc="example",
            ),
            customizable_with_sample_parameters.__name__: Customizable(
                module=__name__,
                name=customizable_with_sample_parameters.__name__,
                func=customizable_with_sample_parameters,
                parameters=SizeParams,
                sample_parameters=SizeParams(width=123, height=456),
                filepath=customizable_with_sample_parameters.__code__.co_filename,
                lineno=customizable_with_sample_parameters.__code__.co_firstlineno,
                short_desc="example_with_sample_params",
            ),
        }
    }
    assert (
        customizable_artifact(SizeParams(width=10, height=20))
        == "customizable_artifact"
    )
    assert (
        customizable_with_sample_parameters(SizeParams(width=10, height=20))
        == "customizable_with_sample_parameters"
    )


def test_customizable_func_without_arg():
    err_msg = "The customizable function should take exactly one argument, but we got {} instead"
    with pytest.raises(ValueError) as exp:

        @customizable
        def func_without_arg():
            pass

    assert exp.value.args[0] == err_msg.format(0)

    with pytest.raises(ValueError) as exp:

        @customizable
        def func_with_too_many_args(params: SizeParams, extra: int = 123):
            pass

    assert exp.value.args[0] == err_msg.format(2)


def test_customizable_func_with_wrong_arg_type():
    err_msg = (
        "The customizable function's parameter argument should be a subclass of pydantic.BaseModel, "
        "but we got <class 'int'> instead"
    )
    with pytest.raises(ValueError) as exp:

        @customizable
        def func_with_wrong_arg_type(val: int):
            pass

    assert exp.value.args[0] == err_msg.format(0)
