import sys
import textwrap

from mr import Cached
from mr import cached
from mr.registry import collect


@cached
def cached_without_params():
    """This is a cached function doc

    - list0
    - list1
    """
    return "cached_without_params"


@cached(short_desc="example_cached")
def cached_with_short_desc():
    """This is an example of cached doc

    - list0
    - list1
    """
    return "cached_with_short_desc"


@cached(desc="OVERRIDDEN_DESC")
def cached_with_desc():
    """This should be overridden by the desc arg"""
    return "cached_with_desc"


def test_collect_cached():
    module = sys.modules[__name__]
    registry = collect([module])
    assert registry.caches == {
        __name__: {
            cached_without_params.__name__: Cached(
                module=__name__,
                name=cached_without_params.__name__,
                func=cached_without_params.__wrapped__,
                desc=textwrap.dedent(
                    "This is a cached function doc\n\n- list0\n- list1"
                ),
                filepath=cached_without_params.__wrapped__.__code__.co_filename,
                lineno=cached_without_params.__wrapped__.__code__.co_firstlineno,
                lookup_funcs=[],
            ),
            cached_with_short_desc.__name__: Cached(
                module=__name__,
                name=cached_with_short_desc.__name__,
                func=cached_with_short_desc.__wrapped__,
                desc=textwrap.dedent(
                    "This is an example of cached doc\n\n- list0\n- list1"
                ),
                short_desc="example_cached",
                filepath=cached_with_short_desc.__wrapped__.__code__.co_filename,
                lineno=cached_with_short_desc.__wrapped__.__code__.co_firstlineno,
                lookup_funcs=[],
            ),
            cached_with_desc.__name__: Cached(
                module=__name__,
                name=cached_with_desc.__name__,
                func=cached_with_desc.__wrapped__,
                desc="OVERRIDDEN_DESC",
                filepath=cached_with_desc.__wrapped__.__code__.co_filename,
                lineno=cached_with_desc.__wrapped__.__code__.co_firstlineno,
                lookup_funcs=[],
            ),
        }
    }
    assert cached_without_params() == "cached_without_params"
    assert cached_with_short_desc() == "cached_with_short_desc"
    assert cached_with_desc() == "cached_with_desc"
