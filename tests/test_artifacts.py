import sys

from mr import Artifact
from mr import artifact
from mr.artifacts.registry import collect


@artifact
def artifact_without_params():
    pass


@artifact(sample=True)
def sample_artifact():
    pass


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
