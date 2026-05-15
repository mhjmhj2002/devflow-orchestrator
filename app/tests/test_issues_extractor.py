from app.github.extractors.issues_extractor import extract_issues_event


def test_extract_issues_raw():
    payload = {
        "repository": {"name": "repo-A"},
        "issue": {"number": 7, "title": "Bug found", "body": "details", "labels": [{"name": "bug"}]},
        "action": "opened",
    }

    data = extract_issues_event(payload)

    assert data["repository"] == "repo-A"
    assert data["issue_number"] == 7
    assert data["issue_title"] == "Bug found"
    assert data["labels"] == [{"name": "bug"}]


def test_extract_issues_normalized():
    payload = {
        "repository": "repo-A",
        "issue_number": 8,
        "issue_title": "Feature",
        "labels": ["enhancement", {"name": "help wanted"}],
    }

    data = extract_issues_event(payload)

    assert data["repository"] == "repo-A"
    assert data["issue_number"] == 8
    assert data["issue_title"] == "Feature"
    # normalized labels become list of dicts
    assert {l["name"] for l in data["labels"]} == {"enhancement", "help wanted"}

