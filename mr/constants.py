import enum


@enum.unique
class CIEnvVars(enum.Enum):
    # the uuid of build job
    MR_BUILD_ID = "MR_BUILD_ID"
    # the number of build job
    MR_BUILD_NUMBER = "MR_BUILD_NUMBER"
    # the git commit hash value
    MR_GIT_COMMIT = "MR_GIT_COMMIT"
    # the full git reference, e.g. refs/heads/master or refs/tags/v1.0.0
    MR_GIT_REF = "MR_GIT_REF"
    # the short name of the git reference, e.g. master or v1.0.0
    MR_GIT_REF_NAME = "MR_GIT_REF_NAME"
    # the name of the repository
    MR_REPOSITORY_NAME = "MR_REPOSITORY_NAME"
    # the username of the repository owner
    MR_REPOSITORY_USERNAME = "MR_REPOSITORY_USERNAME"
    # the full git url of the repository
    MR_REPOSITORY_URL = "MR_REPOSITORY_URL"


# The category for artifacts used in venusian scanning.
MR_ARTIFACTS_CATEGORY = "mr_artifacts"
# The category for customizable used in venusian scanning.
MR_CUSTOMIZABLE_CATEGORY = "mr_customizable"
# The category for cache used in venusian scanning.
MR_CACHE_CATEGORY = "mr_cache"
# The default path to the repo config file.
REPO_CONFIG_PATH = ".makerrepo/config.yaml"
