import sys
import textwrap
import typing

import pytest

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
def cached_with_desc(arg0: int, karg0: str):
    """This should be overridden by the desc arg"""
    return f"cached_with_desc:{arg0}:{karg0}"


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
                store_funcs=[],
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
                store_funcs=[],
            ),
            cached_with_desc.__name__: Cached(
                module=__name__,
                name=cached_with_desc.__name__,
                func=cached_with_desc.__wrapped__,
                desc="OVERRIDDEN_DESC",
                filepath=cached_with_desc.__wrapped__.__code__.co_filename,
                lineno=cached_with_desc.__wrapped__.__code__.co_firstlineno,
                lookup_funcs=[],
                store_funcs=[],
            ),
        }
    }
    assert cached_without_params() == "cached_without_params"
    assert cached_with_short_desc() == "cached_with_short_desc"
    assert cached_with_desc(123, "abc") == "cached_with_desc:123:abc"


@pytest.mark.parametrize(
    "func_name, lookup_funcs, args, kwargs, expected_value",
    [
        ("cached_without_params", [], tuple(), {}, "cached_without_params"),
        (
            "cached_without_params",
            [lambda: "cached_val00"],
            tuple(),
            {},
            "cached_val00",
        ),
        (
            "cached_with_short_desc",
            [lambda: "cached_val01"],
            tuple(),
            {},
            "cached_val01",
        ),
        (
            "cached_with_desc",
            [lambda arg0, karg0: "cached_val02"],
            (123,),
            {"karg0": "abc"},
            "cached_val02",
        ),
        (
            "cached_with_desc",
            [
                lambda arg0, karg0: (
                    "cached_val02" if arg0 == 123 and karg0 == "abc" else None
                )
            ],
            (456,),
            {"karg0": "xyz"},
            "cached_with_desc:456:xyz",
        ),
        (
            "cached_with_desc",
            [
                lambda arg0, karg0: (
                    "cached_val02" if arg0 == 123 and karg0 == "abc" else None
                )
            ],
            (123,),
            {"karg0": "abc"},
            "cached_val02",
        ),
    ],
)
def test_lookup_funcs(
    func_name: str,
    lookup_funcs: list[typing.Callable],
    args: tuple,
    kwargs: dict,
    expected_value: typing.Any,
):
    module = sys.modules[__name__]
    registry = collect([module])

    cached_obj = registry.caches[__name__][func_name]
    cached_obj.lookup_funcs.clear()
    cached_obj.lookup_funcs.extend(lookup_funcs)

    func = globals()[func_name]
    assert func(*args, **kwargs) == expected_value


@pytest.mark.parametrize(
    "func_name, store_funcs, args, kwargs, expected_value",
    [
        ("cached_without_params", [], tuple(), {}, "cached_without_params"),
        (
            "cached_without_params",
            [lambda result: False],
            tuple(),
            {},
            "cached_without_params",
        ),
        (
            "cached_without_params",
            [lambda result: True],
            tuple(),
            {},
            "cached_without_params",
        ),
        (
            "cached_with_short_desc",
            [lambda result: result == "cached_with_short_desc"],
            tuple(),
            {},
            "cached_with_short_desc",
        ),
        (
            "cached_with_desc",
            [lambda result: False, lambda result: True],
            (123,),
            {"karg0": "abc"},
            "cached_with_desc:123:abc",
        ),
        (
            "cached_with_desc",
            [],
            (456,),
            {"karg0": "xyz"},
            "cached_with_desc:456:xyz",
        ),
    ],
)
def test_store_funcs(
    func_name: str,
    store_funcs: list[typing.Callable],
    args: tuple,
    kwargs: dict,
    expected_value: typing.Any,
):
    module = sys.modules[__name__]
    registry = collect([module])

    cached_obj = registry.caches[__name__][func_name]
    cached_obj.lookup_funcs.clear()
    cached_obj.store_funcs.clear()
    cached_obj.store_funcs.extend(store_funcs)

    func = globals()[func_name]
    assert func(*args, **kwargs) == expected_value


def test_store_funcs_receive_result():
    """Store funcs are invoked with the computed result."""
    module = sys.modules[__name__]
    registry = collect([module])
    cached_obj = registry.caches[__name__]["cached_with_desc"]
    cached_obj.lookup_funcs.clear()
    cached_obj.store_funcs.clear()

    received: list[typing.Any] = []
    cached_obj.store_funcs.append(lambda result: received.append(result) or False)

    func = globals()["cached_with_desc"]
    out = func(123, "abc")
    assert out == "cached_with_desc:123:abc"
    assert received == ["cached_with_desc:123:abc"]
