import os
from typing import Iterable, Optional, Set, Tuple

import yaml
from dulwich.errors import NotGitRepository
from dulwich.porcelain import status
from dulwich.repo import Repo


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

def describe_repo(repo_path: str = ".") -> str:
    repo_path = os.path.abspath(repo_path)
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
                "ahead": 0,
                "behind": 0,
            },
            sort_keys=False,
        )

    branch, head_sha = _follow_head(repo)
    is_detached = branch is None

    repo_status = status(repo_path)
    staged_count = sum(len(files) for files in repo_status.staged.values())
    unstaged_count = len(repo_status.unstaged)
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


if __name__ == "__main__":
    print(describe_repo())