import pathlib
import subprocess

import pytest

from mr.build_env import _parse_makerrepo_url
from mr.build_env import BuildEnv
from mr.build_env import BuildEnvVars
from mr.build_env import get_build_version


def _run_git(cwd: pathlib.Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        timeout=5,
    )


def init_git_repo(path: pathlib.Path, *, initial_commit: bool = True) -> None:
    _run_git(path, "init")
    _run_git(path, "config", "user.email", "ci@test.local")
    _run_git(path, "config", "user.name", "CI Test")
    if initial_commit:
        (path / "f").write_text("x")
        _run_git(path, "add", "f")
        _run_git(path, "commit", "-m", "initial")


@pytest.fixture
def git_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """A temporary directory with an initialized git repo and one commit."""
    init_git_repo(tmp_path)
    return tmp_path


@pytest.fixture
def git_repo_with_remote_https(git_repo: pathlib.Path) -> pathlib.Path:
    """Git repo with origin pointing to makerrepo-style HTTPS URL."""
    _run_git(
        git_repo, "remote", "add", "origin", "https://makerrepo.com/r/auser/arepo.git"
    )
    return git_repo


@pytest.fixture
def git_repo_with_remote_ssh(git_repo: pathlib.Path) -> pathlib.Path:
    """Git repo with origin pointing to makerrepo-style SSH URL."""
    _run_git(
        git_repo, "remote", "add", "origin", "git@makerrepo.com:r/bsuser/bsrepo.git"
    )
    return git_repo


# --- from_env ---


def test_from_env_without_vars_returns_none_like():
    """from_env() with no MR_* env vars set yields None for all fields."""
    env = BuildEnv.from_env()
    assert env.build_id is None
    assert env.git_commit is None
    assert env.repository_url is None


def test_from_env_reads_vars(monkeypatch: pytest.MonkeyPatch):
    """from_env() reads MR_* environment variables."""
    monkeypatch.setenv(BuildEnvVars.MR_BUILD_ID.value, "bid")
    monkeypatch.setenv(BuildEnvVars.MR_GIT_COMMIT.value, "abc123")
    monkeypatch.setenv(BuildEnvVars.MR_REPOSITORY_USERNAME.value, "u")
    monkeypatch.setenv(BuildEnvVars.MR_REPOSITORY_NAME.value, "r")
    env = BuildEnv.from_env()
    assert env.build_id == "bid"
    assert env.git_commit == "abc123"
    assert env.repository_username == "u"
    assert env.repository_name == "r"


# --- from_local_git_repo: not in a repo ---


def test_from_local_git_repo_outside_repo_same_as_from_env(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """Outside a git repo, from_local_git_repo() matches from_env() (no git data)."""
    monkeypatch.chdir(tmp_path)
    env = BuildEnv.from_local_git_repo()
    assert env.git_commit is None
    assert env.git_ref is None
    assert env.git_ref_name is None
    assert env.repository_url is None


# --- from_local_git_repo: in a repo ---


def test_from_local_git_repo_fills_commit_and_branch(
    git_repo: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """Inside a repo with a commit and branch, git_commit, git_ref, git_ref_name are filled."""
    monkeypatch.chdir(git_repo)
    env = BuildEnv.from_local_git_repo()
    assert env.git_commit is not None
    assert len(env.git_commit) == 40
    assert env.git_ref is not None
    assert env.git_ref.startswith("refs/heads/")
    assert env.git_ref_name == env.git_ref.removeprefix("refs/heads/")


def test_from_local_git_repo_detached_head_has_commit_no_symbolic_ref(
    git_repo: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """Checking out a tag leaves HEAD detached; we get git_commit but no symbolic ref."""
    monkeypatch.chdir(git_repo)
    _run_git(git_repo, "tag", "v1.0.0")
    _run_git(git_repo, "checkout", "v1.0.0")
    env = BuildEnv.from_local_git_repo()
    assert env.git_commit is not None
    assert env.git_ref is None
    assert env.git_ref_name is None


def test_from_local_git_repo_fills_repository_from_remote_https(
    git_repo_with_remote_https: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """With origin set to makerrepo HTTPS URL, repository_url/username/name are filled."""
    monkeypatch.chdir(git_repo_with_remote_https)
    env = BuildEnv.from_local_git_repo()
    assert env.repository_url == "https://makerrepo.com/r/auser/arepo.git"
    assert env.repository_username == "auser"
    assert env.repository_name == "arepo"


def test_from_local_git_repo_fills_repository_from_remote_ssh(
    git_repo_with_remote_ssh: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """With origin set to makerrepo SSH URL, repository_url/username/name are filled."""
    monkeypatch.chdir(git_repo_with_remote_ssh)
    env = BuildEnv.from_local_git_repo()
    assert env.repository_url == "git@makerrepo.com:r/bsuser/bsrepo.git"
    assert env.repository_username == "bsuser"
    assert env.repository_name == "bsrepo"


def test_from_local_git_repo_env_takes_precedence(
    git_repo_with_remote_https: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """When MR_* env vars are set, they are kept; git only fills unset fields."""
    monkeypatch.chdir(git_repo_with_remote_https)
    monkeypatch.setenv(BuildEnvVars.MR_GIT_COMMIT.value, "env-commit")
    monkeypatch.setenv(BuildEnvVars.MR_REPOSITORY_USERNAME.value, "env-user")
    env = BuildEnv.from_local_git_repo()
    assert env.git_commit == "env-commit"
    assert env.repository_username == "env-user"
    assert env.repository_name == "arepo"
    assert env.repository_url == "https://makerrepo.com/r/auser/arepo.git"


def test_from_local_git_repo_uses_first_remote_when_no_origin(
    git_repo: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """When origin is missing, first remote (by 'git remote') is used for URL."""
    _run_git(
        git_repo, "remote", "add", "upstream", "https://makerrepo.com/r/up/stream.git"
    )
    monkeypatch.chdir(git_repo)
    env = BuildEnv.from_local_git_repo()
    assert env.repository_url == "https://makerrepo.com/r/up/stream.git"
    assert env.repository_username == "up"
    assert env.repository_name == "stream"


# --- _parse_makerrepo_url (URL parsing) ---


@pytest.mark.parametrize(
    "url,expected_username,expected_name",
    [
        ("https://makerrepo.com/r/fangpenlin/tinyrack.git", "fangpenlin", "tinyrack"),
        ("https://makerrepo.com/r/user/repo", "user", "repo"),
        ("git@makerrepo.com:r/auser/arepo.git", "auser", "arepo"),
        ("git@makerrepo.com:bsuser/bsrepo.git", "bsuser", "bsrepo"),
        ("https://other.com/r/u/r.git", "u", "r"),
    ],
)
def test_parse_makerrepo_url(url: str, expected_username: str, expected_name: str):
    """Makerrepo-style URLs yield (username, repository_name)."""
    username, name = _parse_makerrepo_url(url)
    assert username == expected_username
    assert name == expected_name


def test_parse_makerrepo_url_unknown_format_returns_none():
    """URLs with no user/repo-like path segment return (None, None)."""
    assert _parse_makerrepo_url("https://example.com") == (None, None)


# --- get_build_version ---


@pytest.mark.parametrize(
    "env,expected",
    [
        pytest.param(
            BuildEnv(git_ref="refs/tags/v2.0.0", git_ref_name="v2.0.0"),
            "v2.0.0",
            id="tag_returns_tag_name",
        ),
        pytest.param(
            BuildEnv(
                git_ref="refs/tags/v3.0.0",
                git_ref_name="v3.0.0",
                build_number=999,
            ),
            "v3.0.0",
            id="tag_takes_precedence_over_build_number",
        ),
        pytest.param(BuildEnv(build_number=123), "123", id="build_number_when_no_tag"),
        pytest.param(
            BuildEnv(git_commit="a1b2c3d4e5f6"),
            "a1b2",
            id="commit_short_when_no_tag_or_build_number",
        ),
        pytest.param(BuildEnv(), "unknown", id="unknown_when_all_none"),
        pytest.param(
            BuildEnv(
                git_ref="refs/heads/main",
                git_ref_name="main",
                git_commit="abc123456789",
            ),
            "abc1",
            id="branch_uses_commit_not_branch_name",
        ),
    ],
)
def test_get_build_version(env: BuildEnv, expected: str):
    """get_build_version returns expected string for given BuildEnv."""
    assert get_build_version(env=env) == expected


@pytest.mark.parametrize(
    "commit_hash_length,expected",
    [
        pytest.param(4, "a1b2", id="default_4_chars"),
        pytest.param(8, "a1b2c3d4", id="8_chars"),
        pytest.param(1, "a", id="1_char"),
        pytest.param(None, "a1b2c3d4e5f6", id="full_hash"),
    ],
)
def test_get_build_version_commit_hash_length(
    commit_hash_length: int | None, expected: str
):
    """commit_hash_length controls how many leading commit-hash characters are used."""
    env = BuildEnv(git_commit="a1b2c3d4e5f6")
    assert get_build_version(env=env, commit_hash_length=commit_hash_length) == expected
