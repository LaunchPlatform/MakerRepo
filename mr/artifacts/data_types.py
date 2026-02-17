import dataclasses
import typing

from pydantic import BaseModel
from pydantic import Field


@dataclasses.dataclass(frozen=True)
class Artifact:
    module: str
    name: str
    func: typing.Callable
    sample: bool
    cover: bool = False
    desc: str | None = None
    short_desc: str | None = None
    filepath: str | None = None
    lineno: int | None = None
    export_step: bool | None = None
    export_3mf: bool | None = None


@dataclasses.dataclass(frozen=True)
class Customizable:
    module: str
    name: str
    func: typing.Callable
    desc: str | None = None
    short_desc: str | None = None
    filepath: str | None = None
    lineno: int | None = None


class DefaultArtifactConfig(BaseModel):
    """Defaults used when the artifact decorator omits export_step or export_3mf."""

    export_step: bool = Field(
        default=True,
        description="The default `export_step` value for artifacts the value is not set on the artifact decorator.",
    )
    export_3mf: bool = Field(
        default=True,
        description="The default `export_3mf` value for artifacts the value is not set on the artifact decorator.",
    )


class ArtifactsConfig(BaseModel):
    default_config: DefaultArtifactConfig = Field(
        default_factory=DefaultArtifactConfig,
        description="Defaults applied when not set on the artifact decorator",
    )


class RepoConfig(BaseModel):
    """Repo-level config loaded from .makerrepo/config.yaml (or REPO_CONFIG_PATH)."""

    artifacts: ArtifactsConfig | None = Field(
        default=None, description="Artifacts section"
    )
