"""
Git Work Verifier - Validates claimed work against actual git commits

PURPOSE: Prevent false credit claims by verifying work with git evidence
CRITICAL FOR: Entry #025 Integrity pillar
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class WorkClaim:
    """A claim of work completed"""
    agent: str
    file_path: str
    claimed_changes: str
    claimed_timestamp: datetime


@dataclass
class GitEvidence:
    """Git evidence for work"""
    commit_hash: str
    author: str
    timestamp: datetime
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    commit_message: str


@dataclass
class VerificationResult:
    """Result of verifying a work claim"""
    claim: WorkClaim
    verified: bool
    evidence: Optional[GitEvidence]
    confidence: str  # HIGH, MEDIUM, LOW, NONE
    reasoning: str


class GitWorkVerifier:
    """Verify work claims against git history"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
    
    def verify_claim(
        self,
        agent: str,
        file_path: str,
        claimed_changes: str,
        time_window_hours: int = 24
    ) -> VerificationResult:
        """
        Verify if an agent actually did claimed work
        
        Args:
            agent: Agent ID (e.g., "Agent-6")
            file_path: File that was allegedly modified
            claimed_changes: Description of changes
            time_window_hours: How far back to check (default 24h)
        
        Returns:
            VerificationResult with evidence and confidence level
        """
        claim = WorkClaim(
            agent=agent,
            file_path=file_path,
            claimed_changes=claimed_changes,
            claimed_timestamp=datetime.now()
        )
        
        # Get git history for the file
        evidence = self._get_git_evidence(file_path, time_window_hours)
        
        if not evidence:
            return VerificationResult(
                claim=claim,
                verified=False,
                evidence=None,
                confidence="NONE",
                reasoning=f"No git commits found for {file_path} in last {time_window_hours}h"
            )
        
        # Author metadata is self-asserted, and a diff cannot establish
        # semantic completion. Preserve evidence without awarding credit.
        return VerificationResult(
            claim=claim, verified=False, evidence=evidence[0],
            confidence="LOW",
            reasoning="File history observed; agent identity and claimed changes unverified",
        )

    def _get_git_evidence(self, file_path: str, hours: int) -> List[GitEvidence]:
        """Collect one recent literal-file commit; never infer task completion."""
        from pathlib import PurePosixPath
        if (not isinstance(file_path, str) or not file_path
                or len(file_path) > 1024 or "\\" in file_path
                or any(ord(c) < 32 for c in file_path)
                or file_path.startswith(("/", ":"))
                or any(p in ("", ".", "..") for p in file_path.split("/"))
                or PurePosixPath(file_path).is_absolute()):
            raise ValueError("Invalid repository-relative file path")
        if type(hours) is not int or not 1 <= hours <= 168:
            raise ValueError("Invalid time window")
        result = subprocess.run(
            ["git", "--literal-pathspecs", "log", "-1",
             f"--since={hours} hours ago", "--format=%H%x00%an%x00%aI%x00%s",
             "--no-show-signature", "--", file_path],
            cwd=self.repo_path, capture_output=True, text=True,
            errors="replace", check=True, timeout=15,
        )
        if not result.stdout.strip():
            return []
        sha, author, timestamp, message = result.stdout.rstrip("\n").split("\0", 3)
        stats = subprocess.run(
            ["git", "--literal-pathspecs", "diff-tree", "--root", "--first-parent",
             "-m", "-r", "--relative", "--no-commit-id", "--no-renames", "--numstat", "-z",
             sha, "--", file_path],
            cwd=self.repo_path, capture_output=True, check=True, timeout=15,
        )
        files = []
        added = deleted = 0
        for record in stats.stdout.split(b"\0"):
            if not record:
                continue
            plus, minus, name = record.split(b"\t", 2)
            decoded = name.decode("utf-8", errors="surrogateescape")
            if decoded != file_path:
                continue
            files.append(decoded)
            if plus != b"-":
                added += int(plus)
                deleted += int(minus)
        if not files:
            return []
        return [GitEvidence(sha, author, datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                            files, added, deleted, message)]

    def verify_multiple_claims(
        self,
        claims: List[Dict]
    ) -> List[VerificationResult]:
        """Verify multiple work claims at once"""
        results = []
        for claim in claims:
            result = self.verify_claim(
                agent=claim["agent"],
                file_path=claim["file_path"],
                claimed_changes=claim["claimed_changes"],
                time_window_hours=claim.get("time_window_hours", 24)
            )
            results.append(result)
        return results
    
    def generate_report(
        self,
        results: List[VerificationResult]
    ) -> str:
        """Generate human-readable verification report"""
        report = []
        report.append("=" * 80)
        report.append("GIT WORK VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        verified = [r for r in results if r.verified]
        unverified = [r for r in results if not r.verified]
        
        report.append(f"SUMMARY: {len(verified)}/{len(results)} claims verified")
        report.append("")
        
        if verified:
            report.append("✅ VERIFIED CLAIMS:")
            for r in verified:
                report.append(f"  - {r.claim.agent}: {r.claim.file_path}")
                report.append(f"    Evidence: {r.evidence.commit_hash[:8]}")
                report.append(f"    Confidence: {r.confidence}")
                report.append("")
        
        if unverified:
            report.append("❌ UNVERIFIED CLAIMS:")
            for r in unverified:
                report.append(f"  - {r.claim.agent}: {r.claim.file_path}")
                report.append(f"    Reason: {r.reasoning}")
                report.append(f"    Confidence: {r.confidence}")
                report.append("")
        
        return "\n".join(report)


def main():
    """CLI for git work verification"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify work claims against git evidence"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID (e.g., Agent-6)"
    )
    parser.add_argument(
        "--file",
        required=True,
        help="File path to verify"
    )
    parser.add_argument(
        "--changes",
        required=True,
        help="Description of claimed changes"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Time window in hours (default: 24)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format"
    )
    
    args = parser.parse_args()
    
    verifier = GitWorkVerifier()
    result = verifier.verify_claim(
        agent=args.agent,
        file_path=args.file,
        claimed_changes=args.changes,
        time_window_hours=args.hours
    )
    
    if args.json:
        print(json.dumps(asdict(result), default=str, indent=2))
    else:
        print("\n" + "=" * 80)
        print(f"VERIFICATION RESULT: {'✅ VERIFIED' if result.verified else '❌ UNVERIFIED'}")
        print("=" * 80)
        print(f"Agent: {result.claim.agent}")
        print(f"File: {result.claim.file_path}")
        print(f"Claimed: {result.claim.claimed_changes}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
        if result.evidence:
            print(f"\nGit Evidence:")
            print(f"  Commit: {result.evidence.commit_hash[:8]}")
            print(f"  Author: {result.evidence.author}")
            print(f"  Time: {result.evidence.timestamp}")
            print(f"  Changes: +{result.evidence.lines_added} -{result.evidence.lines_deleted}")
        print("")


if __name__ == "__main__":
    main()


