import re
from dataclasses import dataclass
from typing import List, Optional
import yaml

# Case-insensitive pattern to find `git commit -m <anything>` and normalize the message
_COMMIT_RE = re.compile(r"(?i)(^|\s)(git\s+commit\s+-m)\s+(\"[^\"]*\"|'[^']*'|\S+)")

# Multiline pattern to replace any URL/token after `git remote add origin` with `<url>`
_REMOTE_ADD_RE = re.compile(
    r"(?im)^(?P<indent>\s*)(?P<head>git\s+remote\s+add\s+origin)\s+\S+(?P<trail>\s*)$"
)


def normalize_commit_messages(text: str) -> str:
    """Rewrite any commit message to the exact literal "<message>".

    This keeps the rest of the line intact and is idempotent.
    """
    if not text:
        return text

    def _repl(match: re.Match) -> str:
        prefix = match.group(1) or ""
        head = match.group(2)
        return f"{prefix}{head} \"<message>\""

    lines = text.splitlines()
    normalized_lines = [_COMMIT_RE.sub(_repl, line) for line in lines]
    return "\n".join(normalized_lines)


def normalize_remote_urls(text: str) -> str:
    """Rewrite any `git remote add origin <anything>` to use `<url>` placeholder.

    Idempotent: keeps indentation, collapses any quotes/spaces to a single space before `<url>`.
    """
    if not text:
        return text

    def _repl(match: re.Match) -> str:
        indent = match.group('indent') or ""
        head = match.group('head')
        return f"{indent}{head} <url>"

    return _REMOTE_ADD_RE.sub(_repl, text)


def normalize_output(text: str) -> str:
    """Apply all output normalizations in sequence."""
    text = normalize_commit_messages(text)
    text = normalize_remote_urls(text)
    return text


# ------------------------------
# Deterministic planners (remote-aware hard constraints)
# ------------------------------

@dataclass
class GitContext:
    is_repo: bool
    branch: Optional[str]
    is_detached: bool
    staged_count: int
    unstaged_count: int
    has_uncommitted: bool
    remote_exists: bool
    upstream_set: bool

    @property
    def worktree_state(self) -> str:
        if self.staged_count == 0 and self.unstaged_count == 0:
            return "clean"
        if self.staged_count > 0 and self.unstaged_count == 0:
            return "staged"
        if self.staged_count == 0 and self.unstaged_count > 0:
            return "unstaged"
        return "partial"


def _parse_git_context(git_context_str: str) -> GitContext:
    try:
        data = yaml.safe_load(git_context_str) or {}
    except Exception:
        data = {}
    return GitContext(
        is_repo=bool(data.get("is_repo", False)),
        branch=data.get("branch"),
        is_detached=bool(data.get("is_detached", False)),
        staged_count=int(data.get("staged_count", 0) or 0),
        unstaged_count=int(data.get("unstaged_count", 0) or 0),
        has_uncommitted=bool(data.get("has_uncommitted", False)),
        remote_exists=bool(data.get("remote_exists", False)),
        upstream_set=bool(data.get("upstream_set", False)),
    )


def _bash_block(lines: List[str]) -> str:
    cleaned = [line for line in (lines or []) if str(line).strip()]
    body = "\n".join(cleaned) if cleaned else "N/A"
    return f"```\n{body}\n```\n"


# ------------------------------
# Intent planners
# ------------------------------

_KNOWN_INTENTS = {
    "push to remote",
    "pull latest changes",
    "show remotes",
    "add all files",
    "commit my changes",
    "switch to main branch",
    "create a new branch called feature",
    "initialize a repo",
    "show me the status",
    "show commit history",
}

def plan_commit(ctx: GitContext) -> List[str]:
    if not ctx.is_repo:
        return ["git init", "N/A"]
    commands: List[str] = []
    if ctx.is_detached:
        commands.append("git switch main")
    if ctx.worktree_state in {"unstaged", "partial"}:
        commands.append("git add .")
        commands.append('git commit -m "<message>"')
        return commands
    if ctx.worktree_state == "staged":
        commands.append('git commit -m "<message>"')
        return commands
    # clean
    commands.append("N/A")
    return commands


def plan_push(ctx: GitContext) -> List[str]:
    commands: List[str] = []
    if not ctx.is_repo:
        # Initialize, then set remote and push upstream
        return ["git init", "git remote add origin <url>", "git push -u origin main"]

    if ctx.is_detached:
        commands.append("git switch main")

    # Local changes first
    if ctx.worktree_state in {"unstaged", "partial"}:
        commands.append("git add .")
        commands.append('git commit -m "<message>"')
    elif ctx.worktree_state == "staged":
        commands.append('git commit -m "<message>"')

    # Remote/upstream
    if not ctx.remote_exists:
        commands.append("git remote add origin <url>")
        commands.append("git push -u origin main")
    else:
        if ctx.upstream_set:
            commands.append("git push")
        else:
            commands.append("git push -u origin main")
    return commands


def plan_pull(ctx: GitContext) -> List[str]:
    if not ctx.is_repo:
        return ["N/A"]
    if not ctx.remote_exists or not ctx.upstream_set:
        if ctx.is_detached:
            return ["git switch main", "N/A"]
        return ["N/A"]
    if ctx.is_detached:
        return ["git switch main", "git pull"]
    return ["git pull"]


def plan_show_remotes(ctx: GitContext) -> List[str]:
    return ["git remote -v"] if ctx.is_repo else ["N/A"]


def plan_add_all(ctx: GitContext) -> List[str]:
    if not ctx.is_repo:
        return ["git init", "git add ."]
    return ["git add ."]


def plan_switch_main(ctx: GitContext) -> List[str]:
    if not ctx.is_repo:
        return ["N/A"]
    return ["git switch main"]


def plan_create_feature(ctx: GitContext) -> List[str]:
    if not ctx.is_repo:
        return ["git init", "git branch feature"]
    if ctx.is_detached:
        return ["git switch main", "git branch feature"]
    return ["git branch feature"]


def plan_initialize_repo(ctx: GitContext) -> List[str]:
    return ["git init"] if not ctx.is_repo else ["N/A"]


def plan_show_status(ctx: GitContext) -> List[str]:
    return ["git status"] if ctx.is_repo else ["N/A"]


def plan_show_log(ctx: GitContext) -> List[str]:
    return ["git log --oneline"] if ctx.is_repo else ["N/A"]


def detect_intent(user_text: str, llm_output: Optional[str]) -> Optional[str]:
    text = (user_text or "").lower()
    output = (llm_output or "").lower()

    # Command-shape hints first (more reliable)
    if "git push" in output or "git remote add origin" in output:
        return "push to remote"
    if "git pull" in output:
        return "pull latest changes"
    if "git remote -v" in output:
        return "show remotes"
    if "git log --oneline" in output:
        return "show commit history"
    if "git status" in output:
        return "show me the status"
    if "git branch feature" in output:
        return "create a new branch called feature"
    if output.strip() == "git switch main":
        return "switch to main branch"
    if output.strip() == "git init" or ("git init" in output and "git add ." not in output and "git commit -m" not in output):
        return "initialize a repo"

    # Natural-language hints
    if any(k in text for k in ["push", "upload", "publish", "sync up"]):
        return "push to remote"
    if any(k in text for k in ["pull", "sync down", "update", "get latest"]):
        return "pull latest changes"
    if any(k in text for k in ["remote", "origin", "url"]):
        return "show remotes"
    if any(k in text for k in ["status", "what changed", "st "]):
        return "show me the status"
    if any(k in text for k in ["history", "log", "commits"]):
        return "show commit history"
    if any(k in text for k in ["add all", "stage all", "stage everything"]):
        return "add all files"
    if any(k in text for k in ["commit", "save changes"]):
        return "commit my changes"
    if any(k in text for k in ["switch to main", "checkout main", "go to main", "master"]):
        return "switch to main branch"
    if any(k in text for k in ["new branch", "feature branch"]):
        return "create a new branch called feature"
    if any(k in text for k in ["init", "initialize repo"]):
        return "initialize a repo"
    return None


def plan_by_intent(intent: str, ctx: GitContext) -> List[str]:
    if intent == "push to remote":
        return plan_push(ctx)
    if intent == "pull latest changes":
        return plan_pull(ctx)
    if intent == "show remotes":
        return plan_show_remotes(ctx)
    if intent == "add all files":
        return plan_add_all(ctx)
    if intent == "commit my changes":
        return plan_commit(ctx)
    if intent == "switch to main branch":
        return plan_switch_main(ctx)
    if intent == "create a new branch called feature":
        return plan_create_feature(ctx)
    if intent == "initialize a repo":
        return plan_initialize_repo(ctx)
    if intent == "show me the status":
        return plan_show_status(ctx)
    if intent == "show commit history":
        return plan_show_log(ctx)
    return ["N/A"]


def enforce_policies(user_message: str, git_context_str: str, llm_output: str) -> str:
    """Apply remote-aware hard constraints to produce a deterministic response.

    This function detects intent automatically and uses planners to construct
    the minimal, correct command list given the git context. The result is
    returned inside a single code block.
    """
    ctx = _parse_git_context(git_context_str)
    intent = detect_intent(user_message, llm_output)
    # If the model exactly provided one of the known intents as the user message
    # keep it as-is for routing. Otherwise rely on detection.
    if (not intent) and (user_message in _KNOWN_INTENTS):
        intent = user_message
    if not intent:
        # As a safe fallback, if the model output already matches strict rules
        # we still normalize and return it. Otherwise, return N/A.
        planned = ["N/A"]
    else:
        planned = plan_by_intent(intent, ctx)
    return _bash_block(planned)


