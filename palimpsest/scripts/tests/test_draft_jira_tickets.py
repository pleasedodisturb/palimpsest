"""Tests for publishing/draft_jira_tickets.py — draft building and markdown preview."""


def test_build_drafts_basic(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [
        {"summary": "Fix login bug", "description": "Users can't log in", "issue_type": "Bug"},
    ]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert len(drafts) == 1
    fields = drafts[0]["fields"]
    assert fields["project"]["key"] == "PROJ"
    assert fields["summary"] == "Fix login bug"
    assert fields["description"] == "Users can't log in"
    assert fields["issuetype"]["name"] == "Bug"


def test_build_drafts_default_type(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [{"summary": "Some task"}]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert drafts[0]["fields"]["issuetype"]["name"] == "Task"


def test_build_drafts_default_summary(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [{}]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert "Draft ticket 1" in drafts[0]["fields"]["summary"]


def test_build_drafts_with_priority(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [{"summary": "Urgent", "priority": "High"}]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert drafts[0]["fields"]["priority"]["name"] == "High"


def test_build_drafts_without_priority(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [{"summary": "Normal task"}]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert "priority" not in drafts[0]["fields"]


def test_build_drafts_with_labels(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [{"summary": "Task", "labels": ["backend", "automation"]}]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert drafts[0]["fields"]["labels"] == ["backend", "automation"]


def test_build_drafts_with_components(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [{"summary": "Task", "components": ["api", "frontend"]}]
    drafts = mod.build_drafts(candidates, "PROJ")
    components = drafts[0]["fields"]["components"]
    assert len(components) == 2
    assert components[0] == {"name": "api"}
    assert components[1] == {"name": "frontend"}


def test_build_drafts_multiple(load_module):
    mod = load_module("publishing/draft_jira_tickets.py")
    candidates = [
        {"summary": "Task 1"},
        {"summary": "Task 2"},
        {"summary": "Task 3"},
    ]
    drafts = mod.build_drafts(candidates, "PROJ")
    assert len(drafts) == 3


def test_write_markdown(load_module, tmp_path):
    mod = load_module("publishing/draft_jira_tickets.py")
    drafts = [
        {
            "fields": {
                "project": {"key": "PROJ"},
                "summary": "Fix the thing",
                "issuetype": {"name": "Bug"},
                "priority": {"name": "High"},
                "labels": ["urgent"],
                "components": [{"name": "backend"}],
                "description": "It's broken.",
            }
        }
    ]
    output = tmp_path / "preview.md"
    mod.write_markdown(drafts, str(output))

    content = output.read_text()
    assert "# Draft Jira Tickets" in content
    assert "Fix the thing" in content
    assert "**Project**: PROJ" in content
    assert "**Type**: Bug" in content
    assert "**Priority**: High" in content
    assert "**Labels**: urgent" in content
    assert "**Components**: backend" in content
    assert "It's broken." in content
