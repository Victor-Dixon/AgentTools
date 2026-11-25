"""Compatibility interface for local Git evidence, not task authorization."""
from datetime import datetime, timezone

from tools.deprecated.git_work_verifier import GitWorkVerifier


def check_commits_today(file_pattern):
    """Return recent literal-file evidence dated today in UTC."""
    evidence = GitWorkVerifier()._get_git_evidence(file_pattern, 48)
    today = datetime.now(timezone.utc).date()
    return [
        {"commit_hash": item.commit_hash, "author": item.author,
         "timestamp": item.timestamp.isoformat(),
         "files_changed": item.files_changed,
         "commit_message": item.commit_message}
        for item in evidence
        if item.timestamp.astimezone(timezone.utc).date() == today
    ]


def verify_work_exists(file_patterns, agent_name=None):
    """Require evidence for every literal file; never authenticate an agent."""
    if not isinstance(file_patterns, list) or not file_patterns:
        return False
    observed = [check_commits_today(path) for path in file_patterns]
    return agent_name is None and all(observed)
