from typing import Iterable, Optional, Tuple
import yaml
from dulwich.errors import NotGitRepository
from dulwich.porcelain import status
from dulwich.repo import Repo
from pathlib import Path
from gitmate.config import DEFAULT_REPO_STATUS_PATH

# _follow_head returns the current branch name when HEAD points to a branch, otherwise None, letting the caller detect a detached state.
def _follow_head(repo: Repo) -> Tuple[Optional[str], bytes]:
    ref, sha = repo.refs.follow(b"HEAD")
    refs: Iterable[Optional[bytes]]
    if isinstance(ref, (list, tuple)):
        refs = ref
    else:
        refs = (ref,)
    for candidate in refs:
        if candidate and candidate.startswith(b"refs/heads/"):
            return candidate.rsplit(b"/", 1)[-1].decode("utf-8"), sha
    return None, sha

def describe_repo() -> str:
    repo_path = str(Path.cwd())
    try:
        repo = Repo(repo_path)
    except NotGitRepository:
        return yaml.safe_dump(
            {
                "is_repo": False,
                "branch": None,
                "is_detached": False,
                "staged_count": 0,
                "unstaged_count": 0,
                "has_uncommitted": False,
                "remote_exists": False,
                "upstream_set": False,
            },
            sort_keys=False,
        )

    branch, head_sha = _follow_head(repo)
    is_detached = branch is None

    repo_status = status(repo_path)
    staged_count = sum(len(files) for files in repo_status.staged.values())
    unstaged_count = len(repo_status.unstaged) + len(repo_status.untracked)
    has_uncommitted = bool(
        staged_count or unstaged_count or repo_status.untracked
    )

    remote_refs = [ref for ref in repo.refs if ref.startswith(b"refs/remotes/")]
    remote_exists = bool(remote_refs)

    upstream_ref = None
    upstream_set = False

    if not is_detached and branch:
        config = repo.get_config_stack()
        section = (b"branch", branch.encode("utf-8"))
        try:
            remote_name = config.get(section, b"remote").decode("utf-8")
            merge_ref = config.get(section, b"merge")
            upstream_ref = b"refs/remotes/%b/%b" % (
                remote_name.encode("utf-8"),
                merge_ref.rsplit(b"/", 1)[-1],
            )
            upstream_set = upstream_ref in repo.refs
        except KeyError:
            remote_name = None
            merge_ref = None

    repo.close()
    return yaml.safe_dump(
        {
            "is_repo": True,
            "branch": branch or head_sha.decode("utf-8"),
            "is_detached": is_detached,
            "staged_count": staged_count,
            "unstaged_count": unstaged_count,
            "has_uncommitted": has_uncommitted,
            "remote_exists": remote_exists,
            "upstream_set": upstream_set,
        },
        sort_keys=False,
    )


def get_git_context() -> str:
    """
    Get the current git repository context as a formatted YAML string.
    Also saves the context to .gitmate/repo_status.yaml for caching.
    Uses the current working directory to locate the git repository.
    """
    
    yaml_content = describe_repo()
    git_context = yaml.safe_load(yaml_content) or {}
    
    # Save to .gitmate/repo_status.yaml for caching
    DEFAULT_REPO_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEFAULT_REPO_STATUS_PATH.open("w", encoding="utf-8") as handle:
        handle.write(yaml_content)
    
    # Return formatted string
    git_context_str = yaml.dump(
        git_context, 
        default_flow_style=False, 
        allow_unicode=True, 
        sort_keys=False
    ).strip() or "No git context available."
    
    return git_context_str



