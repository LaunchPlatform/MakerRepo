import sys
import textwrap

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


def test_collect():
    module = sys.modules[__name__]
    registry = collect([module])
    assert registry.customizables == {
        __name__: {
            customizable_artifact.__name__: Customizable(
                module=__name__,
                name=customizable_artifact.__name__,
                func=customizable_artifact,
                filepath=customizable_artifact.__code__.co_filename,
                lineno=customizable_artifact.__code__.co_firstlineno,
                desc=textwrap.dedent("This is an example of doc\n\n- list0\n- list1"),
                short_desc="example",
            ),
        }
    }
    assert (
        customizable_artifact(SizeParams(width=10, height=20))
        == "customizable_artifact"
    )
