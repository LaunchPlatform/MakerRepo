import json

import pytest

from mr.exceptions import FieldError
from mr.exceptions import GeneratorValidationError


def test_generator_validation_error_single_message():
    """Single message is stored and used as exception message."""
    err = GeneratorValidationError("Too many parts")
    assert err.messages == ("Too many parts",)
    assert str(err) == "Too many parts"
    with pytest.raises(GeneratorValidationError, match="Too many parts") as exc_info:
        raise err
    assert exc_info.value.messages == ("Too many parts",)
    assert exc_info.value.fields == []


def test_generator_validation_error_multiple_messages():
    """Multiple messages are stored and joined in str()."""
    err = GeneratorValidationError("Too many parts", "Invalid angle range")
    assert err.messages == ("Too many parts", "Invalid angle range")
    assert str(err) == "Too many parts; Invalid angle range"
    assert err.fields == []


def test_generator_validation_error_fields_require_field_error():
    """Field errors must be FieldError instances, not raw tuples."""
    fe1 = FieldError(
        ("window", "size", "width"),
        "Width must be an integer greater than 10",
    )
    fe2 = FieldError(
        ("window", "size", "height"),
        "Height must be an integer instead of an float",
    )
    err = GeneratorValidationError(
        "Too many parts",
        "Invalid angle range",
        fields=[fe1, fe2],
    )
    assert err.messages == ("Too many parts", "Invalid angle range")
    assert len(err.fields) == 2
    assert err.fields[0] == fe1
    assert err.fields[1] == fe2
    assert "window.size.width" in str(err)
    assert "window.size.height" in str(err)


def test_generator_validation_error_fields_as_field_error():
    """Field errors passed as FieldError instances are stored as-is (same instances)."""
    fe1 = FieldError(
        ("window", "size", "width"), "Width must be an integer greater than 10"
    )
    fe2 = FieldError(
        ("window", "size", "height"), "Height must be an integer instead of an float"
    )
    err = GeneratorValidationError(
        "Too many parts",
        "Invalid angle range",
        fields=[fe1, fe2],
    )
    assert err.messages == ("Too many parts", "Invalid angle range")
    assert err.fields == [fe1, fe2]
    assert err.fields[0] is fe1
    assert err.fields[1] is fe2


def test_generator_validation_error_no_messages_with_fields():
    """Can have only field errors, no general messages."""
    fe = FieldError(("x",), "Must be positive")
    err = GeneratorValidationError(fields=[fe])
    assert err.messages == ()
    assert len(err.fields) == 1
    assert err.fields[0] is fe
    assert err.fields[0].path == ("x",)
    assert err.fields[0].message == "Must be positive"
    assert "Field errors" in str(err)


def test_generator_validation_error_empty():
    """No messages and no fields yields generic str."""
    err = GeneratorValidationError()
    assert err.messages == ()
    assert err.fields == []
    assert str(err) == "Generator validation failed"


def test_field_error_equality_and_repr():
    """FieldError supports equality and has a clear repr."""
    fe = FieldError(("a", "b"), "message")
    assert fe == FieldError(("a", "b"), "message")
    assert fe != FieldError(("a", "b"), "other")
    assert fe != FieldError(("a", "c"), "message")
    assert "FieldError" in repr(fe)
    assert "('a', 'b')" in repr(fe)
    assert "message" in repr(fe)


def test_raise_generator_validation_error_with_fields():
    """Raising and catching preserves messages and fields."""
    with pytest.raises(GeneratorValidationError) as exc_info:
        raise GeneratorValidationError(
            "Too many parts",
            "Invalid angle range",
            fields=[
                FieldError(
                    ("window", "size", "width"),
                    "Width must be an integer greater than 10",
                ),
                FieldError(
                    ("window", "size", "height"),
                    "Height must be an integer instead of an float",
                ),
            ],
        )
    e = exc_info.value
    assert e.messages == ("Too many parts", "Invalid angle range")
    assert len(e.fields) == 2
    assert e.fields[0].path == ("window", "size", "width")
    assert e.fields[0].message == "Width must be an integer greater than 10"
    assert e.fields[1].path == ("window", "size", "height")
    assert e.fields[1].message == "Height must be an integer instead of an float"


def test_field_error_to_dict_from_dict():
    """FieldError round-trips via to_dict/from_dict."""
    fe = FieldError(("window", "size", "width"), "Width must be positive")
    d = fe.to_dict()
    assert d == {
        "path": ["window", "size", "width"],
        "message": "Width must be positive",
    }
    assert FieldError.from_dict(d) == fe


def test_generator_validation_error_to_dict_from_dict():
    """GeneratorValidationError round-trips via to_dict/from_dict."""
    err = GeneratorValidationError(
        "Too many parts",
        "Invalid angle range",
        fields=[
            FieldError(("window", "size", "width"), "Width must be positive"),
            FieldError(("window", "size", "height"), "Height must be positive"),
        ],
    )
    d = err.to_dict()
    assert d == {
        "messages": ["Too many parts", "Invalid angle range"],
        "fields": [
            {"path": ["window", "size", "width"], "message": "Width must be positive"},
            {
                "path": ["window", "size", "height"],
                "message": "Height must be positive",
            },
        ],
    }
    restored = GeneratorValidationError.from_dict(d)
    assert restored.messages == err.messages
    assert restored.fields == err.fields


def test_generator_validation_error_json_roundtrip():
    """GeneratorValidationError can be dumped to JSON and parsed back."""
    err = GeneratorValidationError(
        "Too many parts",
        fields=[FieldError(("a", "b"), "Bad value")],
    )
    payload = json.dumps(err.to_dict())
    parsed = json.loads(payload)
    restored = GeneratorValidationError.from_dict(parsed)
    assert restored.messages == err.messages
    assert len(restored.fields) == 1
    assert restored.fields[0].path == ("a", "b")
    assert restored.fields[0].message == "Bad value"


@pytest.mark.parametrize(
    "bad_field",
    [
        ("window.size.width", "not a FieldError"),
        {"path": ["x"], "message": "dict, not FieldError"},
        "a plain string",
        42,
        None,
    ],
    ids=["tuple", "dict", "str", "int", "None"],
)
def test_generator_validation_error_rejects_non_field_error(bad_field):
    """fields list items that are not FieldError instances raise TypeError."""
    with pytest.raises(TypeError, match="Field error must be a FieldError instance"):
        GeneratorValidationError("msg", fields=[bad_field])


def test_generator_validation_error_rejects_mixed_field_errors():
    """TypeError is raised even when valid FieldErrors precede the bad item."""
    fe = FieldError(("a",), "ok")
    with pytest.raises(TypeError, match="Field error must be a FieldError instance"):
        GeneratorValidationError("msg", fields=[fe, "not a FieldError"])


def test_generator_validation_error_from_value_error():
    """from_value_error builds GeneratorValidationError with ValueError message."""
    ve = ValueError("Invalid input")
    err = GeneratorValidationError.from_value_error(ve)
    assert err.messages == ("Invalid input",)
    assert err.fields == []
    assert str(err) == "Invalid input"


def test_generator_validation_error_from_value_error_empty_message():
    """from_value_error handles ValueError with empty message."""
    ve = ValueError("")
    err = GeneratorValidationError.from_value_error(ve)
    assert err.messages == ("",)
    assert err.fields == []
