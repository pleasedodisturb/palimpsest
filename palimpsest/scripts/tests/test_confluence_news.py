"""Tests for publishing/push_confluence_news.py — daily panel and status gen."""


def test_generate_daily_panel_basic(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    panel = mod.generate_daily_panel("2024-03-15", ["Item one", "Item two"])
    assert "March 15, 2024" in panel
    assert "<li>Item one</li>" in panel
    assert "<li>Item two</li>" in panel
    assert 'ac:name="panel"' in panel


def test_generate_daily_panel_with_highlight(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    panel = mod.generate_daily_panel("2024-03-15", ["Item"], highlight="Big news!")
    assert "<strong>Big news!</strong>" in panel


def test_generate_daily_panel_no_highlight(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    panel = mod.generate_daily_panel("2024-03-15", ["Item"])
    assert "<strong>" not in panel


def test_generate_current_status_with_jira_data(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    jira_data = {"open_tickets": 15, "in_progress": 8, "done": 42}
    html = mod.generate_current_status_section("2024-03-15", jira_data)
    assert "Current Status" in html
    assert "March 15, 2024" in html
    assert "<table>" in html
    assert "Open Tickets" in html
    assert "15" in html
    assert "42" in html


def test_generate_current_status_no_jira(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    html = mod.generate_current_status_section("2024-03-15")
    assert "No Jira data available" in html
    assert "<table>" not in html


def test_manage_weekly_archive_nothing_old(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    # Panel from yesterday — should NOT be archived
    content = (
        '<ac:structured-macro ac:name="panel"><ac:rich-text-body>'
        '<h3>March 14, 2024</h3><ul><li>Recent</li></ul>'
        '</ac:rich-text-body></ac:structured-macro>'
    )
    result = mod.manage_weekly_archive(content, "2024-03-15")
    assert result == content  # Nothing to archive


def test_manage_weekly_archive_old_panel(load_module):
    mod = load_module("publishing/push_confluence_news.py")
    # Panel from 10 days ago — should be archived
    content = (
        '<ac:structured-macro ac:name="panel"><ac:rich-text-body>'
        '<h3>March 01, 2024</h3><ul><li>Old item</li></ul>'
        '</ac:rich-text-body></ac:structured-macro>'
    )
    result = mod.manage_weekly_archive(content, "2024-03-15")
    assert "Archived Updates" in result
    assert 'ac:name="expand"' in result
