from app.github.extractors.issue_comment_extractor import extract_issue_comment


def test_extract_issue_comment_raw():
    payload = {
        "repository": {"name": "repo-name"},
        "issue": {"number": 123},
        "comment": {"id": 999, "body": "hello", "user": {"login": "alice"}},
        "action": "created",
    }

    data = extract_issue_comment(payload)

    assert data["repository"] == "repo-name"
    assert data["issue_number"] == 123
    assert data["comment_body"] == "hello"
    assert data["comment_user"] == "alice"
    assert data["comment_id"] == 999


def test_extract_issue_comment_normalized():
    payload = {
        "repository": "repo-name",
        "issue_number": 321,
        "comment_body": "hi",
        "comment_user": "bob",
        "comment_id": 111,
        "action": "edited",
    }

    data = extract_issue_comment(payload)

    assert data["repository"] == "repo-name"
    assert data["issue_number"] == 321
    assert data["comment_body"] == "hi"
    assert data["comment_user"] == "bob"
    assert data["comment_id"] == 111

