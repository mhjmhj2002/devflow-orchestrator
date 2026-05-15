# app/schemas/github.py

from pydantic import BaseModel
from typing import List, Optional


class GitHubIssue(BaseModel):
    number: int
    title: str
    labels: Optional[List[dict]] = None


class GitHubRepository(BaseModel):
    name: str


class GitHubWebhookPayload(BaseModel):
    action: str | None = None
    repository: GitHubRepository | None = None
    issue: GitHubIssue | None = None