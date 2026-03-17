"""Tests for automation/read_agent_markers.py — ID parsing and type detection."""


def test_parse_drive_id_from_file_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    url = "https://drive.google.com/file/d/1aBcDeFg/view"
    assert mod.parse_drive_id(url) == "1aBcDeFg"


def test_parse_drive_id_from_doc_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    url = "https://docs.google.com/document/d/abcXYZ-123/edit"
    assert mod.parse_drive_id(url) == "abcXYZ-123"


def test_parse_drive_id_from_folder_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    url = "https://drive.google.com/drive/folders/1aBcDeFgHiJk"
    assert mod.parse_drive_id(url) == "1aBcDeFgHiJk"


def test_parse_drive_id_query_param(load_module):
    mod = load_module("automation/read_agent_markers.py")
    url = "https://drive.google.com/open?id=abc123xyz"
    assert mod.parse_drive_id(url) == "abc123xyz"


def test_parse_drive_id_bare(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.parse_drive_id("1aBcDeFgHiJkLmNo") == "1aBcDeFgHiJkLmNo"


def test_parse_drive_id_too_short(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.parse_drive_id("short") is None


def test_parse_drive_id_invalid(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.parse_drive_id("not a valid thing!!!") is None


def test_parse_confluence_id_from_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    url = "https://mycompany.atlassian.net/wiki/pages/12345678"
    assert mod.parse_confluence_id(url) == "12345678"


def test_parse_confluence_id_page_id_param(load_module):
    mod = load_module("automation/read_agent_markers.py")
    url = "https://mycompany.atlassian.net/wiki/pages/viewpage.action?pageId=99887766"
    assert mod.parse_confluence_id(url) == "99887766"


def test_parse_confluence_id_bare(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.parse_confluence_id("12345678") == "12345678"


def test_parse_confluence_id_not_numeric(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.parse_confluence_id("not-a-number") is None


def test_detect_type_confluence_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.detect_type("https://myco.atlassian.net/wiki/pages/123") == "confluence"


def test_detect_type_confluence_keyword(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.detect_type("https://confluence.example.com/page/123") == "confluence"


def test_detect_type_drive_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.detect_type("https://drive.google.com/file/d/abc") == "drive"


def test_detect_type_docs_url(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.detect_type("https://docs.google.com/document/d/abc") == "drive"


def test_detect_type_numeric_id(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.detect_type("12345678") == "confluence"


def test_detect_type_alphanumeric_id(load_module):
    mod = load_module("automation/read_agent_markers.py")
    assert mod.detect_type("aBcDeFgHiJkLmNo") == "drive"
