"""Tests for sync/gdrive_sync.py — file categorization and query building."""


def test_categorize_file_planning(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("Q4 Roadmap 2024.docx") == "planning"
    assert mod.categorize_file("project-timeline.pdf") == "planning"


def test_categorize_file_architecture(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("System Architecture.md") == "architecture"
    assert mod.categorize_file("RFC-001-new-api.md") == "architecture"
    assert mod.categorize_file("Technical Design Doc.pdf") == "architecture"


def test_categorize_file_product(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("PRD - New Feature.docx") == "product"
    assert mod.categorize_file("Requirements Spec v2.pdf") == "product"


def test_categorize_file_security(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("Security Review Q3.docx") == "security"
    assert mod.categorize_file("SOX Compliance Report.pdf") == "security"


def test_categorize_file_reports(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("Weekly Status Report.md") == "reports"
    assert mod.categorize_file("Monthly Update March.docx") == "reports"


def test_categorize_file_meetings(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("Meeting Notes 2024-03-15.md") == "meetings"
    assert mod.categorize_file("Standup Notes.txt") == "meetings"
    assert mod.categorize_file("Retro Actions.md") == "meetings"


def test_categorize_file_uncategorized(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("random_file.txt") == "uncategorized"
    assert mod.categorize_file("photo.png") == "uncategorized"


def test_categorize_file_case_insensitive(load_module):
    mod = load_module("sync/gdrive_sync.py")
    assert mod.categorize_file("ARCHITECTURE.md") == "architecture"
    assert mod.categorize_file("weekly REPORT.docx") == "reports"


def test_build_keyword_query_single(load_module):
    mod = load_module("sync/gdrive_sync.py")
    result = mod._build_keyword_query(["roadmap"], include_trashed=False)
    assert "fullText contains 'roadmap'" in result
    assert "trashed=false" in result


def test_build_keyword_query_multiple(load_module):
    mod = load_module("sync/gdrive_sync.py")
    result = mod._build_keyword_query(["roadmap", "design"], include_trashed=False)
    assert "fullText contains 'roadmap'" in result
    assert "fullText contains 'design'" in result
    assert " or " in result
    assert "trashed=false" in result


def test_build_keyword_query_include_trashed(load_module):
    mod = load_module("sync/gdrive_sync.py")
    result = mod._build_keyword_query(["test"], include_trashed=True)
    assert "trashed" not in result


def test_build_keyword_query_empty(load_module):
    mod = load_module("sync/gdrive_sync.py")
    result = mod._build_keyword_query([], include_trashed=False)
    assert result == "trashed=false"


def test_build_keyword_query_escapes_quotes(load_module):
    mod = load_module("sync/gdrive_sync.py")
    result = mod._build_keyword_query(["it's a test"], include_trashed=True)
    assert "it\\'s a test" in result
