"""Minimal Git client wrapper used by code generation workflow.

This uses the system `git` CLI. It performs only constrained operations and
is intentionally minimal for safety: clone, checkout -b, commit, push.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional


class GitClient:

    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = Path(work_dir) if work_dir else None

    def run(self, cmd, cwd=None):
        cwd = str(cwd or self.work_dir or Path.cwd())
        proc = subprocess.run(cmd, cwd=cwd, shell=False, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr

    def clone(self, repo_url: str, dest: str):
        dest_path = Path(dest)
        if dest_path.exists():
            return 0, f"destination exists: {dest}", ""

        cmd = ["git", "clone", repo_url, dest]
        return self.run(cmd, cwd=Path.cwd())

    def checkout_new_branch(self, repo_path: str, branch_name: str):
        cmd = ["git", "checkout", "-b", branch_name]
        return self.run(cmd, cwd=repo_path)

    def add_commit_push(self, repo_path: str, message: str, branch: str = None):
        cmds = [
            (["git", "add", "-A"], repo_path),
            (["git", "commit", "-m", message], repo_path),
        ]

        for cmd, cwd in cmds:
            code, out, err = self.run(cmd, cwd=cwd)
            if code != 0:
                return code, out, err

        # push
        push_cmd = ["git", "push", "-u", "origin", branch] if branch else ["git", "push"]
        return self.run(push_cmd, cwd=repo_path)

