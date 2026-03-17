"""Tests for content/link_extractor.py — URL extraction, categorization, dedup."""

import json
import tempfile
from pathlib import Path


def test_categorize_confluence(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://mycompany.atlassian.net/wiki/spaces/PROJ/pages/123") == "confluence"


def test_categorize_jira(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://mycompany.atlassian.net/browse/PROJ-123") == "jira"


def test_categorize_google_docs(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://docs.google.com/document/d/abc123/edit") == "google_docs"


def test_categorize_google_sheets(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://docs.google.com/spreadsheets/d/abc/edit") == "google_sheets"


def test_categorize_google_drive(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://drive.google.com/file/d/abc123") == "google_drive"


def test_categorize_github(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://github.com/user/repo") == "github"
    assert mod.categorize_link("https://user.github.io/project") == "github"


def test_categorize_slack(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://myworkspace.slack.com/archives/C123") == "slack"


def test_categorize_figma(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://www.figma.com/file/abc/Design") == "figma"


def test_categorize_notion(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://www.notion.so/page-abc123") == "notion"
    assert mod.categorize_link("https://team.notion.site/page") == "notion"


def test_categorize_other(load_module):
    mod = load_module("content/link_extractor.py")
    assert mod.categorize_link("https://example.com/whatever") == "other"


def test_extract_from_text_bare_urls(load_module):
    mod = load_module("content/link_extractor.py")
    text = "Check https://github.com/user/repo and https://example.com"
    links = mod.extract_from_text(text)
    assert len(links) == 2
    assert links[0]["url"] == "https://github.com/user/repo"
    assert links[0]["category"] == "github"
    assert links[1]["url"] == "https://example.com"


def test_extract_from_text_deduplicates(load_module):
    mod = load_module("content/link_extractor.py")
    text = "https://example.com and again https://example.com"
    links = mod.extract_from_text(text)
    assert len(links) == 1


def test_extract_from_text_strips_trailing_punctuation(load_module):
    mod = load_module("content/link_extractor.py")
    text = "See https://example.com. Also https://other.com,"
    links = mod.extract_from_text(text)
    assert links[0]["url"] == "https://example.com"
    assert links[1]["url"] == "https://other.com"


def test_extract_from_text_with_source(load_module):
    mod = load_module("content/link_extractor.py")
    links = mod.extract_from_text("https://example.com", source_file="test.md")
    assert links[0]["source"] == "test.md"


def test_extract_from_markdown_named_links(load_module):
    mod = load_module("content/link_extractor.py")
    text = "Check [My Project](https://github.com/user/repo) for details"
    links = mod.extract_from_markdown(text)
    assert len(links) == 1
    assert links[0]["title"] == "My Project"
    assert links[0]["url"] == "https://github.com/user/repo"
    assert links[0]["category"] == "github"


def test_extract_from_markdown_mixed(load_module):
    mod = load_module("content/link_extractor.py")
    text = "[Named](https://a.com) and bare https://b.com"
    links = mod.extract_from_markdown(text)
    assert len(links) == 2
    assert links[0]["title"] == "Named"
    assert links[1]["title"] == ""


def test_extract_from_markdown_no_duplicate_of_named_link(load_module):
    mod = load_module("content/link_extractor.py")
    text = "[Link](https://example.com)"
    links = mod.extract_from_markdown(text)
    # Should not appear twice (once as named, once as bare)
    assert len(links) == 1


def test_extract_strings_recursive(load_module):
    mod = load_module("content/link_extractor.py")
    data = {"a": "https://example.com", "b": [{"c": "https://other.com"}]}
    acc = []
    mod._extract_strings(data, acc)
    assert "https://example.com" in acc
    assert "https://other.com" in acc


def test_extract_from_json(load_module, tmp_path):
    mod = load_module("content/link_extractor.py")
    data = {"url": "https://github.com/user/repo", "nested": {"link": "https://example.com"}}
    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps(data))
    links = mod.extract_from_json(str(json_file))
    assert len(links) == 2


def test_deduplicate_links_merges_sources(load_module):
    mod = load_module("content/link_extractor.py")
    links = [
        {"url": "https://example.com", "title": "Example", "source": "a.md", "category": "other"},
        {"url": "https://example.com", "title": "", "source": "b.md", "category": "other"},
    ]
    result = mod.deduplicate_links(links)
    assert len(result) == 1
    assert result[0]["title"] == "Example"
    assert "a.md" in result[0]["sources"]
    assert "b.md" in result[0]["sources"]


def test_deduplicate_links_preserves_first_title(load_module):
    mod = load_module("content/link_extractor.py")
    links = [
        {"url": "https://example.com", "title": "", "source": "a.md", "category": "other"},
        {"url": "https://example.com", "title": "Better Title", "source": "b.md", "category": "other"},
    ]
    result = mod.deduplicate_links(links)
    assert result[0]["title"] == "Better Title"


def test_deduplicate_links_different_urls(load_module):
    mod = load_module("content/link_extractor.py")
    links = [
        {"url": "https://a.com", "title": "A", "source": "x.md", "category": "other"},
        {"url": "https://b.com", "title": "B", "source": "x.md", "category": "other"},
    ]
    result = mod.deduplicate_links(links)
    assert len(result) == 2


def test_generate_markdown_report(load_module):
    mod = load_module("content/link_extractor.py")
    links = [
        {"url": "https://github.com/user/repo", "title": "My Repo", "category": "github", "sources": ["a.md"]},
        {"url": "https://example.com", "title": "Example", "category": "other", "sources": []},
    ]
    report = mod.generate_markdown_report(links)
    assert "# Link Index" in report
    assert "Github" in report
    assert "My Repo" in report
    assert "Total unique links: 2" in report


def test_scan_directory(load_module, tmp_path):
    mod = load_module("content/link_extractor.py")
    md = tmp_path / "test.md"
    md.write_text("[Link](https://example.com)\nhttps://github.com/user/repo")
    links = mod.scan_directory(str(tmp_path))
    assert len(links) >= 2
