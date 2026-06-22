"""
Commit updated detections.json and push to origin/main.

Assumes the working directory is the repo root, and that git credentials
are configured (e.g. via Windows Credential Manager or a deploy key).
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DETECTIONS_JSON = REPO_ROOT / "web" / "data" / "detections.json"


def _run(args: list[str], cwd: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def commit_and_push(dry_run: bool = False) -> None:
    """
    Stage detections.json, commit with a timestamped message, and push.

    Set dry_run=True to stage + commit but skip the push (useful for testing).
    """
    _run(["git", "add", str(DETECTIONS_JSON.relative_to(REPO_ROOT))])

    status = _run(["git", "status", "--porcelain"])
    if not status:
        print("No changes to commit — detections.json is unchanged.")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit_msg = f"data: update detections ({timestamp})"
    _run(["git", "commit", "-m", commit_msg])
    print(f"Committed: {commit_msg}")

    if dry_run:
        print("dry_run=True — skipping push.")
        return

    _run(["git", "push", "origin", "main"])
    print("Pushed to origin/main. Cloudflare Pages deploy triggered.")


if __name__ == "__main__":
    commit_and_push()
