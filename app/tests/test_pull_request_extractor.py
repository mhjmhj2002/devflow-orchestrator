from app.github.extractors.pull_request_extractor import extract_pull_request


def test_extract_pull_request_raw():
    payload = {
        "repository": {"name": "repo-PR"},
        "pull_request": {"number": 42, "title": "Add feature", "body": "impl", "labels": [{"name": "feature"}]},
        "action": "opened",
    }

    data = extract_pull_request(payload)

    assert data["repository"] == "repo-PR"
    assert data["pr_number"] == 42
    assert data["pr_title"] == "Add feature"
    assert data["labels"] == [{"name": "feature"}]


def test_extract_pull_request_normalized():
    payload = {
        "repository": "repo-PR",
        "pr_number": 43,
        "pr_title": "Fix bug",
        "labels": ["bug", {"name": "urgent"}],
    }

    data = extract_pull_request(payload)

    assert data["repository"] == "repo-PR"
    assert data["pr_number"] == 43
    assert data["pr_title"] == "Fix bug"
    assert {l["name"] for l in data["labels"]} == {"bug", "urgent"}

