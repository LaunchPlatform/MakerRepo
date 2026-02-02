import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class Artifact:
    module: str
    name: str
    func: typing.Callable
    sample: bool
    cover: bool = False
    desc: str | None = None
    filepath: str | None = None
    lineno: int | None = None
