"""Tests for publishing/push_confluence_weekly.py — week calculations and content gen."""

import re


def test_get_week_info_basic(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    info = mod.get_week_info("2024-01-15")  # Monday
    assert info["cw"] == 3
    assert info["year"] == 2024
    assert info["week_start"] == "2024-01-15"
    assert info["week_end"] == "2024-01-19"
    assert "CW3 2024" == info["label"]


def test_get_week_info_mid_week(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    info = mod.get_week_info("2024-01-17")  # Wednesday
    assert info["cw"] == 3
    assert info["week_start"] == "2024-01-15"  # Still Monday


def test_get_week_info_date_range(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    info = mod.get_week_info("2024-06-10")
    assert "Jun" in info["date_range"]
    assert "2024" in info["date_range"]


def test_get_week_info_year_boundary(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    info = mod.get_week_info("2024-01-01")  # ISO week 1 of 2024
    assert info["year"] == 2024
    assert info["cw"] == 1


def test_generate_weekly_summary_default(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    week_info = {"label": "CW10 2024", "date_range": "Mar 04 - Mar 08, 2024"}
    html = mod.generate_weekly_summary(week_info)
    assert "CW10 2024" in html
    assert "Mar 04 - Mar 08, 2024" in html
    assert "Achievements" in html
    assert 'ac:name="panel"' in html


def test_generate_weekly_summary_with_context(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    week_info = {"label": "CW10 2024", "date_range": "Mar 04 - Mar 08, 2024"}
    context = {
        "achievements": ["Shipped feature X", "Fixed bug Y"],
        "blockers": ["Waiting on API access"],
        "next_week": ["Start integration testing"],
    }
    html = mod.generate_weekly_summary(week_info, context)
    assert "Shipped feature X" in html
    assert "Fixed bug Y" in html
    assert "Blockers" in html
    assert "Waiting on API access" in html
    assert "Next Week" in html
    assert "Start integration testing" in html


def test_generate_weekly_summary_no_blockers(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    week_info = {"label": "CW10 2024", "date_range": "test"}
    context = {"achievements": ["Done"], "blockers": [], "next_week": []}
    html = mod.generate_weekly_summary(week_info, context)
    assert "Blockers" not in html
    assert "Next Week" not in html


def test_count_weekly_panels(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    content = '<h2>CW10 2024</h2>...<h2>CW11 2024</h2>...<h2>CW12 2024</h2>'
    assert mod.count_weekly_panels(content) == 3


def test_count_weekly_panels_empty(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    assert mod.count_weekly_panels("<p>No panels here</p>") == 0


def test_archive_old_weeks_under_limit(load_module):
    mod = load_module("publishing/push_confluence_weekly.py")
    content = '<ac:structured-macro ac:name="panel"><h2>CW10 2024</h2></ac:structured-macro>'
    result = mod.archive_old_weeks(content, max_weeks=8)
    assert result == content  # No change when under limit
