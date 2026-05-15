# app/events/validator.py

from app.core.logger import logger
from app.events.contracts.issue_events import IssueOpenedEvent, IssueCommentCreatedEvent
from app.github.extractors.issue_comment_extractor import extract_issue_comment
from app.github.extractors.issues_extractor import extract_issues_event
from app.github.extractors.pull_request_extractor import extract_pull_request


class EventValidator:

    @staticmethod
    def validate(event_name: str, payload: dict):

        logger.info(f"Validating event: {event_name}")

        # Support issues and issue_comment events
        if event_name not in ("issues", "issue_comment"):
            return None, "unsupported event"

        try:
            # Support two payload shapes:
            # 1) raw GitHub payload: { repository: {name}, issue: {...} }
            # 2) normalized payload: { repository: "name", issue_number: n, issue_title: "...", labels: [...] }

            repository = payload.get("repository")
            issue = payload.get("issue")

            # handle event types using extractors to normalize payloads
            if event_name == "issue_comment":
                data = extract_issue_comment(payload)

                repo_name = data.get("repository")
                if not repo_name:
                    return None, "missing repository"

                repository_safe = {"name": repo_name}

                issue_number = data.get("issue_number")

                comment_safe = {
                    "id": data.get("comment_id") or 0,
                    "body": data.get("comment_body") or "",
                    "user": {"login": data.get("comment_user") or ""}
                }

                event = IssueCommentCreatedEvent(
                    repository=repository_safe,
                    issue_number=issue_number,
                    comment=comment_safe,
                    service=payload.get("service")
                )


                return event, None

            if event_name == "issues":
                # normalize issues payloads
                data = extract_issues_event(payload)

                repo_name = data.get("repository")
                if not repo_name:
                    return None, "missing repository"

                repository_safe = {"name": repo_name}

                issue_safe = {
                    "number": data.get("issue_number"),
                    "title": data.get("issue_title"),
                    "body": data.get("issue_body"),
                    "labels": data.get("labels") or []
                }

                service = payload.get("service")

                event = IssueOpenedEvent(
                    repository=repository_safe,
                    issue=issue_safe,
                    service=service
                )

                return event, None

            if event_name == "pull_request":
                data = extract_pull_request(payload)

                repo_name = data.get("repository")
                if not repo_name:
                    return None, "missing repository"

                # map pull request into IssueOpenedEvent-like structure for now
                repository_safe = {"name": repo_name}

                issue_safe = {
                    "number": data.get("pr_number"),
                    "title": data.get("pr_title"),
                    "labels": data.get("labels") or []
                }

                service = payload.get("service")

                event = IssueOpenedEvent(
                    repository=repository_safe,
                    issue=issue_safe,
                    service=service
                )

                return event, None

            # detect normalized payload shape: repository is a string and issue_number/title present
            if isinstance(payload.get("repository"), str) and (payload.get("issue_number") or payload.get("issue_title")):
                # normalized payload case
                repo_name = payload.get("repository")
                repository_safe = {"name": repo_name}

                issue_safe = {
                    "number": payload.get("issue_number"),
                    "title": payload.get("issue_title"),
                    "labels": []
                }

                # normalize labels if present (could be list of strings or list of dicts)
                labels_raw = payload.get("labels") or []
                normalized_labels = []
                for l in labels_raw:
                    if isinstance(l, dict):
                        name = l.get("name")
                    else:
                        name = str(l)
                    if name:
                        normalized_labels.append({"name": name})

                issue_safe["labels"] = normalized_labels

                service = payload.get("service")

                event = IssueOpenedEvent(
                    repository=repository_safe,
                    issue=issue_safe,
                    service=service
                )

                return event, None

            # legacy/raw payload case
            if not repository or not issue:
                return None, "missing repository or issue"

            # issue['labels'] may be None (pydantic optional); normalize to empty list
            labels = issue.get("labels") or []

            service = None
            for label in labels:
                # label may be dict or string
                name = label.get("name") if isinstance(label, dict) else str(label)
                if "service:" in name:
                    parts = name.split(":", 1)
                    if len(parts) > 1:
                        service = parts[1]

            # ensure we pass non-None lists to the Pydantic model
            issue_safe = dict(issue) if isinstance(issue, dict) else issue
            issue_safe = issue_safe or {}
            issue_safe["labels"] = issue_safe.get("labels") or []

            repository_safe = dict(repository) if isinstance(repository, dict) else repository

            event = IssueOpenedEvent(
                repository=repository_safe,
                issue=issue_safe,
                service=service
            )

            return event, None

        except Exception as e:
            logger.exception(e)
            return None, str(e)

