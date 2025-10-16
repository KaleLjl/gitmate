import re


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


