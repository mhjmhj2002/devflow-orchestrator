# app/events/contracts/issue_events.py

from pydantic import BaseModel
from typing import Optional, List


class IssueLabel(BaseModel):
    name: str


class Repository(BaseModel):
    name: str


class Issue(BaseModel):
    number: int
    title: str
    labels: List[IssueLabel] = []


class IssueOpenedEvent(BaseModel):
    # versioned event_type, format: <resource>.<action>
    event_type: str = "issues.opened"

    repository: Repository
    issue: Issue

    service: Optional[str] = None


class CommentAuthor(BaseModel):
    login: str


class IssueComment(BaseModel):
    id: int
    body: str
    user: CommentAuthor


class IssueCommentCreatedEvent(BaseModel):
    # event_type format: issue_comment.created
    event_type: str = "issue_comment.created"

    repository: Repository
    issue_number: int
    comment: IssueComment

    service: Optional[str] = None


