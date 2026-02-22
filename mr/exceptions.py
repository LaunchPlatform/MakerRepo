import dataclasses
from typing import Union


@dataclasses.dataclass(frozen=True, slots=True)
class FieldError:
    """A validation error at a specific JSON path."""

    path: tuple[str, ...]
    message: str

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict (path as list)."""
        return {"path": list(self.path), "message": self.message}

    @classmethod
    def from_dict(cls, d: dict) -> "FieldError":
        """Parse from a dict (e.g. from JSON)."""
        return cls(tuple(d["path"]), d["message"])


FieldErrorItem = Union[FieldError, tuple[tuple[str, ...], str]]


def _normalize_field_error(item: FieldErrorItem) -> FieldError:
    if isinstance(item, FieldError):
        return item
    path, message = item
    return FieldError(tuple(path), message)


class GeneratorValidationError(ValueError):
    """Error for generator input data validation failures.

    Accepts one or more general error messages and optionally a list of
    field-level errors (path + message). Field errors can be passed as
    FieldError instances or as (path_tuple, message) pairs; they are
    stored as FieldError instances on the .fields attribute.
    """

    def __init__(
        self,
        *messages: str,
        fields: list[FieldErrorItem] | None = None,
    ):
        super().__init__(messages[0] if messages else "")
        self.messages: tuple[str, ...] = messages
        self.fields: list[FieldError] = (
            [_normalize_field_error(item) for item in fields] if fields else []
        )

    def __str__(self) -> str:
        parts: list[str] = []
        if self.messages:
            parts.append("; ".join(self.messages))
        if self.fields:
            field_strs = [f"{'.'.join(f.path)}: {f.message}" for f in self.fields]
            parts.append("Field errors: " + "; ".join(field_strs))
        return " ".join(parts) if parts else "Generator validation failed"

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict for dumping as JSON payload."""
        return {
            "messages": list(self.messages),
            "fields": [f.to_dict() for f in self.fields],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GeneratorValidationError":
        """Parse from a dict (e.g. from JSON)."""
        messages = tuple(d.get("messages", ()))
        fields = [FieldError.from_dict(f) for f in d.get("fields", [])]
        return cls(*messages, fields=fields)

    @classmethod
    def from_value_error(cls, err: ValueError) -> "GeneratorValidationError":
        """Build a GeneratorValidationError from a ValueError (message becomes single message)."""
        return cls(str(err))
