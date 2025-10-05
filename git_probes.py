# stdlib
import json, os, sys
from dulwich import porcelain # higher level helpers
from dulwich.repo import Repo # low-level repo object for structure / metadata / config.
from dulwich.errors import NotGitRepository # o gracefully handle “not in a repo”.
 
# dulwich
from dulwich import porcelain
from dulwich.repo import Repo
from dulwich.errors import NotGitRepository

# ---------- repo discovery + basic rev-parse ----------
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

# ---------- current branch (handles detached HEAD) ----------
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
# ---------- git status  ----------
def status_porcelain(repo):
    """
    Return a list of entries like:
      {"xy": "A ", "path": "file"}   # staged add
      {"xy": " M", "path": "file"}   # unstaged modify
      {"xy": "??", "path": "file"}   # untracked
    """
    st = porcelain.status(repo)

    def _to_str(p):
        return p.decode() if isinstance(p, (bytes, bytearray)) else str(p)

    out = []

    # staged is a dict: {'add': set, 'modify': set, 'delete': set}
    for kind, paths in st.staged.items():
        code = {"add": "A", "modify": "M", "delete": "D"}.get(kind, "?")
        for p in sorted(paths, key=_to_str):
            out.append({"xy": f"{code} ", "path": _to_str(p)})

    # unstaged: modified-but-not-staged
    for p in sorted(st.unstaged, key=_to_str):
        out.append({"xy": " M", "path": _to_str(p)})

    # untracked
    for p in sorted(st.untracked, key=_to_str):
        out.append({"xy": "??", "path": _to_str(p)})

    return out
# ---------- remote -v ----------
def list_remotes(repo):
    """
    Return a list of remotes with fetch/push URLs:
      [{"name": "origin", "fetch": "...", "push": "..."}, ...]
    """
    cfg = repo.get_config()
    rems = []
    for sect in cfg.sections():
        if len(sect) == 2 and sect[0] == b"remote":
            name = sect[1].decode()
            url = cfg.get(sect, b"url")
            pushurl = cfg.get(sect, b"pushurl")
            rems.append({
                "name": name,
                "fetch": url.decode() if url else None,
                "push": (pushurl.decode() if pushurl else (url.decode() if url else None)),
            })
    return rems

# ---------- upstream branch (@{u}) ----------
def upstream_ref(repo, branch_name: str):
    """
    Return a dict with:
      short: upstream branch short name (e.g., 'main')
      remote: remote name (e.g., 'origin')
      fullref: full remote ref (e.g., 'refs/remotes/origin/main')
    Empty strings if not set.
    """
    if not branch_name:
        return {"short": "", "remote": "", "fullref": ""}

    try:
        merge_ref = porcelain.get_branch_merge(repo, branch_name.encode())  # e.g. b"refs/heads/main"
        remote_name = porcelain.get_branch_remote(repo)  # e.g. b"origin"
        if not (merge_ref and remote_name):
            return {"short": "", "remote": "", "fullref": ""}

        short = merge_ref.decode().replace("refs/heads/", "", 1)
        full_remote = f"refs/remotes/{remote_name.decode()}/{short}"
        return {"short": short, "remote": remote_name.decode(), "fullref": full_remote}
    except Exception:
        return {"short": "", "remote": "", "fullref": ""}

# ---------- ahead/behind relative to upstream ----------
def ahead_behind(repo, local_branch: str, upstream_fullref: str):
    """
    Return {'ahead': N, 'behind': M} by comparing the local branch with the upstream.
    """
    try:
        if not local_branch or not upstream_fullref:
            return {"ahead": 0, "behind": 0}

        local_full = f"refs/heads/{local_branch}"
        if local_full not in repo.refs or upstream_fullref not in repo.refs:
            return {"ahead": 0, "behind": 0}

        ahead = len(list(porcelain.rev_list(repo, [local_full], [upstream_fullref])))
        behind = len(list(porcelain.rev_list(repo, [upstream_fullref], [local_full])))
        return {"ahead": ahead, "behind": behind}
    except Exception:
        return {"ahead": 0, "behind": 0}



# ---  writer to a json file---
def write_partial_json(cwd=".", out_name="git_info.json"):
    repo = discover_repo(cwd)
    info = {}

    if not repo:
        info["is_inside_work_tree"] = False
    else:
        inside = is_inside_work_tree(repo)
        info["is_inside_work_tree"] = inside
        info["toplevel"] = show_toplevel(repo) if inside else ""

        br = current_branch(repo)
        info["branch"] = br

        up = upstream_ref(repo, br) if br else {"short": "", "remote": "", "fullref": ""}
        info["upstream"] = up

        info["ahead_behind"] = ahead_behind(repo, br, up.get("fullref", ""))

        info["git_status"] = status_porcelain(repo)
        info["remotes"] = list_remotes(repo)

    out_path = os.path.join(cwd, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(out_path)




if __name__ == "__main__":
    # Run in current directory (or pass a path)
    write_partial_json(sys.argv[1] if len(sys.argv) > 1 else ".")
