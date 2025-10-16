import re


# Case-insensitive pattern to find `git commit -m <anything>` and normalize the message
_COMMIT_RE = re.compile(r"(?i)(^|\s)(git\s+commit\s+-m)\s+(\"[^\"]*\"|'[^']*'|\S+)")


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


