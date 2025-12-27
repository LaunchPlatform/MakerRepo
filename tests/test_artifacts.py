import sys

from mr import Artifact
from mr import artifact
from mr.artifacts.registry import collect


@artifact
def artifact_without_params():
    return "artifact_without_params"


@artifact(sample=True)
def sample_artifact():
    return "sample_artifact"


def test_collect():
    module = sys.modules[__name__]
    registry = collect([module])
    assert registry.artifacts == {
        __name__: {
            artifact_without_params.__name__: Artifact(
                module=__name__,
                name=artifact_without_params.__name__,
                func=artifact_without_params,
                sample=False,
            ),
            sample_artifact.__name__: Artifact(
                module=__name__,
                name=sample_artifact.__name__,
                func=sample_artifact,
                sample=True,
            ),
        }
    }
    assert artifact_without_params() == "artifact_without_params"
    assert sample_artifact() == "sample_artifact"
