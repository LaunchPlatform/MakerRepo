import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class Artifact:
    module: str
    name: str
    func: typing.Callable
    sample: bool
