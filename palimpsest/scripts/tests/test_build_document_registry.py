"""Tests for content/build_document_registry.py — classification, dedup, markdown gen."""

import json


def test_classify_doc_type_match(load_module):
    mod = load_module("content/build_document_registry.py")
    rules = {
        "design": ["design", "architecture", "rfc"],
        "plan": ["plan", "roadmap"],
    }
    entry = {"title": "System Architecture v2"}
    assert mod.classify_doc_type(entry, rules) == "design"


def test_classify_doc_type_no_match(load_module):
    mod = load_module("content/build_document_registry.py")
    rules = {"design": ["design"]}
    entry = {"title": "Meeting Notes"}
    assert mod.classify_doc_type(entry, rules) == "other"


def test_classify_doc_type_case_insensitive(load_module):
    mod = load_module("content/build_document_registry.py")
    rules = {"plan": ["roadmap"]}
    entry = {"title": "Q4 ROADMAP"}
    assert mod.classify_doc_type(entry, rules) == "plan"


def test_classify_status(load_module):
    mod = load_module("content/build_document_registry.py")
    rules = {"draft": ["draft", "wip"], "final": ["approved"]}
    assert mod.classify_status({"title": "Draft RFC"}, rules) == "draft"
    assert mod.classify_status({"title": "Approved Plan"}, rules) == "final"
    assert mod.classify_status({"title": "Random"}, rules) == "unknown"


def test_classify_importance(load_module):
    mod = load_module("content/build_document_registry.py")
    rules = {"critical": ["critical", "must-read"], "high": ["important"]}
    assert mod.classify_importance({"title": "Critical Security Review"}, rules) == "critical"
    assert mod.classify_importance({"title": "Normal Doc"}, rules) == "normal"


def test_classify_importance_skips_empty_keywords(load_module):
    mod = load_module("content/build_document_registry.py")
    rules = {"critical": ["critical"], "normal": []}
    assert mod.classify_importance({"title": "Normal Doc"}, rules) == "normal"


def test_canonicalize_url_strips_trailing_slash(load_module):
    mod = load_module("content/build_document_registry.py")
    assert mod.canonicalize_url("https://example.com/page/") == "https://example.com/page"


def test_canonicalize_url_strips_fragment(load_module):
    mod = load_module("content/build_document_registry.py")
    assert mod.canonicalize_url("https://example.com/page#section") == "https://example.com/page"


def test_canonicalize_url_lowercases(load_module):
    mod = load_module("content/build_document_registry.py")
    assert mod.canonicalize_url("https://Example.COM/Page") == "https://example.com/page"


def test_dedupe_entries(load_module):
    mod = load_module("content/build_document_registry.py")
    entries = [
        {"title": "Doc A", "url": "https://example.com/doc"},
        {"title": "Doc A Dup", "url": "https://example.com/doc/"},
        {"title": "Doc B", "url": "https://other.com/page"},
    ]
    result = mod.dedupe_entries(entries)
    assert len(result) == 2


def test_dedupe_entries_keeps_first(load_module):
    mod = load_module("content/build_document_registry.py")
    entries = [
        {"title": "First", "url": "https://example.com/doc", "source": "drive"},
        {"title": "Second", "url": "https://example.com/doc", "source": "confluence"},
    ]
    result = mod.dedupe_entries(entries)
    assert result[0]["title"] == "First"
    assert result[0]["source"] == "drive"


def test_generate_markdown_with_metadata(load_module):
    mod = load_module("content/build_document_registry.py")
    entries = [
        {
            "title": "Design Doc",
            "url": "https://example.com/design",
            "source": "drive",
            "type": "design",
            "status": "draft",
            "importance": "high",
            "modified": "2024-01-15T12:00:00Z",
        }
    ]
    config = {"group_by": "type", "include_metadata": True}
    md = mod.generate_markdown(entries, config)
    assert "# Document Registry" in md
    assert "Design" in md
    assert "[Design Doc]" in md
    assert "draft" in md
    assert "high" in md


def test_generate_markdown_without_metadata(load_module):
    mod = load_module("content/build_document_registry.py")
    entries = [
        {"title": "Doc", "url": "https://example.com", "type": "other"},
    ]
    config = {"group_by": "type", "include_metadata": False}
    md = mod.generate_markdown(entries, config)
    assert "- [Doc]" in md
    assert "| Title |" not in md


def test_generate_markdown_groups_by_key(load_module):
    mod = load_module("content/build_document_registry.py")
    entries = [
        {"title": "A", "url": "https://a.com", "source": "drive"},
        {"title": "B", "url": "https://b.com", "source": "confluence"},
    ]
    config = {"group_by": "source", "include_metadata": False}
    md = mod.generate_markdown(entries, config)
    assert "## Drive" in md or "## drive" in md.lower()
    assert "## Confluence" in md or "## confluence" in md.lower()


def test_collect_local_link_index_list_format(load_module, tmp_path):
    mod = load_module("content/build_document_registry.py")
    data = [
        {"url": "https://example.com", "title": "Example"},
        {"url": "https://other.com"},
    ]
    index_file = tmp_path / "links.json"
    index_file.write_text(json.dumps(data))
    entries = mod.collect_local_link_index(str(index_file))
    assert len(entries) == 2
    assert entries[0]["source"] == "local_index"
    assert entries[1]["title"] == "https://other.com"


def test_collect_local_link_index_dict_format(load_module, tmp_path):
    mod = load_module("content/build_document_registry.py")
    data = {"https://example.com": "Example Site"}
    index_file = tmp_path / "links.json"
    index_file.write_text(json.dumps(data))
    entries = mod.collect_local_link_index(str(index_file))
    assert len(entries) == 1
    assert entries[0]["title"] == "Example Site"


def test_collect_local_link_index_missing_file(load_module):
    mod = load_module("content/build_document_registry.py")
    entries = mod.collect_local_link_index("/nonexistent/path.json")
    assert entries == []
