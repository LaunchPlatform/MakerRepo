import dataclasses
import enum
import os
import re
import subprocess
from typing import Self

# Pattern for makerrepo-style URLs: .../r/username/reponame or .../r/username/reponame.git
_MAKERREPO_URL_RE = re.compile(
    r"(?:https?://[^/]+/r/|(?://[^/]+/)?)([^/]+)/([^/]+?)(?:\.git)?$"
)


def _git_run(args: list[str]) -> str | None:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0 or not result.stdout:
        return None
    return result.stdout.strip() or None


def _git_rev_parse_head() -> str | None:
    return _git_run(["git", "rev-parse", "HEAD"])


def _git_symbolic_ref_head() -> str | None:
    return _git_run(["git", "symbolic-ref", "-q", "HEAD"])


def _git_ref_name_from_ref(ref: str | None) -> str | None:
    if not ref:
        return None
    for prefix in ("refs/heads/", "refs/tags/"):
        if ref.startswith(prefix):
            return ref[len(prefix) :]
    return ref


def _git_remote_url() -> str | None:
    url = _git_run(["git", "remote", "get-url", "origin"])
    if url:
        return url
    remotes = _git_run(["git", "remote"])
    if not remotes:
        return None
    first_remote = remotes.split()[0]
    return _git_run(["git", "remote", "get-url", first_remote])


def _parse_makerrepo_url(url: str) -> tuple[str | None, str | None]:
    # Support https://makerrepo.com/r/user/repo.git or git@host:user/repo.git
    url = url.rstrip("/")
    # SSH: git@makerrepo.com:r/fangpenlin/tinyrack.git or git@makerrepo.com:fangpenlin/tinyrack.git
    if url.startswith("git@"):
        parts = url.split(":", 1)
        if len(parts) == 2:
            path = parts[1]
            if path.startswith("r/"):
                path = path[2:]
            segments = path.replace(".git", "").rstrip("/").split("/")
            if len(segments) >= 2:
                return segments[0], segments[1]
            if len(segments) == 1:
                return segments[0], None
    m = _MAKERREPO_URL_RE.search(url)
    if m:
        return m.group(1), m.group(2)
    return None, None


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


@dataclasses.dataclass(frozen=True)
class CIEnv:
    build_id: str | None = None
    build_number: int | None = None
    git_commit: str | None = None
    git_ref: str | None = None
    git_ref_name: str | None = None
    repository_name: str | None = None
    repository_username: str | None = None
    repository_url: str | None = None

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            build_id=os.getenv(CIEnvVars.MR_BUILD_ID.value),
            build_number=os.getenv(CIEnvVars.MR_BUILD_NUMBER.value),
            git_commit=os.getenv(CIEnvVars.MR_GIT_COMMIT.value),
            git_ref=os.getenv(CIEnvVars.MR_GIT_REF.value),
            git_ref_name=os.getenv(CIEnvVars.MR_GIT_REF_NAME.value),
            repository_name=os.getenv(CIEnvVars.MR_REPOSITORY_NAME.value),
            repository_username=os.getenv(CIEnvVars.MR_REPOSITORY_USERNAME.value),
            repository_url=os.getenv(CIEnvVars.MR_REPOSITORY_URL.value),
        )

    @classmethod
    def from_local_git_repo(cls) -> Self:
        env = cls.from_env()
        # Fill only values that are not already set; use replace() for a new instance
        replacements: dict[str, str | None] = {}
        if env.git_commit is None:
            replacements["git_commit"] = _git_rev_parse_head()
        if env.git_ref is None:
            replacements["git_ref"] = _git_symbolic_ref_head()
        git_ref = replacements.get("git_ref", env.git_ref)
        if env.git_ref_name is None:
            replacements["git_ref_name"] = _git_ref_name_from_ref(git_ref)
        if env.repository_url is None:
            replacements["repository_url"] = _git_remote_url()
        url = replacements.get("repository_url", env.repository_url)
        if url:
            username, name = _parse_makerrepo_url(url)
            if env.repository_username is None and username:
                replacements["repository_username"] = username
            if env.repository_name is None and name:
                replacements["repository_name"] = name
        return dataclasses.replace(env, **replacements)
