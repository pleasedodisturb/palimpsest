"""Tests for content/download_doc.py — Doc ID extraction."""

import pytest


def test_extract_doc_id_from_url(load_module):
    mod = load_module("content/download_doc.py")
    url = "https://docs.google.com/document/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/edit"
    assert mod.extract_doc_id(url) == "1aBcDeFgHiJkLmNoPqRsTuVwXyZ"


def test_extract_doc_id_from_url_no_edit(load_module):
    mod = load_module("content/download_doc.py")
    url = "https://docs.google.com/document/d/abc123"
    assert mod.extract_doc_id(url) == "abc123"


def test_extract_doc_id_bare_id(load_module):
    mod = load_module("content/download_doc.py")
    assert mod.extract_doc_id("1aBcDeFgHiJkLmNoPqRsTuVwXyZ") == "1aBcDeFgHiJkLmNoPqRsTuVwXyZ"


def test_extract_doc_id_with_params(load_module):
    mod = load_module("content/download_doc.py")
    url = "https://docs.google.com/document/d/abc-123_XY/edit?usp=sharing"
    assert mod.extract_doc_id(url) == "abc-123_XY"


def test_extract_doc_id_invalid_exits(load_module):
    mod = load_module("content/download_doc.py")
    with pytest.raises(SystemExit):
        mod.extract_doc_id("not a valid url or id!!!")
