# stdlib
import json, os, sys
from dulwich import porcelain # higher level helpers
from dulwich.repo import Repo # low-level repo object for structure / metadata / config.
from dulwich.errors import NotGitRepository # o gracefully handle “not in a repo”.
 
# dulwich
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.errors import NotGitRepository

# ---------- Step 2: repo discovery + basic rev-parse ----------
def discover_repo(cwd="."):
    """Return a dulwich Repo if we're inside a git repo; else None."""
    try:
        return Repo.discover(cwd)
    except NotGitRepository:
        return None

def is_inside_work_tree(repo):
    """True if this is a non-bare repo with a working tree."""
    return bool(repo and repo.has_index())

def show_toplevel(repo):
    """Absolute path to the repository root (work tree)."""
    # dulwich Repo usually points at the control dir (.git); parent is the root
    path = repo.controldir()  # may be str or bytes depending on version
    path = os.fsdecode(path)
    return os.path.abspath(os.path.dirname(path))

# ---------- Step 3: current branch (handles detached HEAD) ----------
def current_branch(repo):
    """
    Return the current branch name as a string, or "" if detached/unknown.
    Uses porcelain.active_branch when available; falls back to following HEAD.
    """
    try:
        b = porcelain.active_branch(repo)  # may return bytes or None when detached
        if b:
            return b.decode() if isinstance(b, (bytes, bytearray)) else str(b)
    except Exception:
        pass

    # Fallback: follow HEAD reference to a local branch like refs/heads/main
    try:
        chain, _ = repo.refs.follow(b"HEAD")
        # chain often like [b'HEAD', b'refs/heads/main']
        for ref in chain:
            if isinstance(ref, (bytes, bytearray)) and ref.startswith(b"refs/heads/"):
                return ref.split(b"/", 2)[-1].decode()
    except Exception:
        pass

    # Detached HEAD or cannot resolve
    return ""


# --- Update the writer to include "branch" ---
def write_partial_json(cwd=".", out_name="git_info.json"):
    repo = discover_repo(cwd)
    info = {}

    if not repo:
        info["is_inside_work_tree"] = False
    else:
        inside = is_inside_work_tree(repo)
        info["is_inside_work_tree"] = inside
        if inside:
            info["toplevel"] = show_toplevel(repo)
        else:
            info["toplevel"] = ""

        # NEW: current branch
        info["branch"] = current_branch(repo)

    out_path = os.path.join(cwd, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(out_path)

if __name__ == "__main__":
    # Run in current directory (or pass a path)
    write_partial_json(sys.argv[1] if len(sys.argv) > 1 else ".")
