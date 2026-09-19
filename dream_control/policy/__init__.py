"""Policy engine: what a fleet agent is and is not authorised to do."""

from .branch import PRESERVATION_HOLDS, branch_disposition, cleanup_allowed
from .duplication import DuplicationVerdict, check_duplication
from .publish import PublishDecision, publish_allowed
from .worktree import worktree_disposition

__all__ = [
    "PRESERVATION_HOLDS",
    "branch_disposition",
    "cleanup_allowed",
    "DuplicationVerdict",
    "check_duplication",
    "PublishDecision",
    "publish_allowed",
    "worktree_disposition",
]
