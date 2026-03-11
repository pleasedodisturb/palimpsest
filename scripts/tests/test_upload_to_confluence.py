"""Tests for content/upload_to_confluence.py — markdown to Confluence conversion."""


def test_inline_bold(load_module):
    mod = load_module("content/upload_to_confluence.py")
    assert mod._inline("**bold**") == "<strong>bold</strong>"


def test_inline_italic(load_module):
    mod = load_module("content/upload_to_confluence.py")
    assert mod._inline("*italic*") == "<em>italic</em>"


def test_inline_code(load_module):
    mod = load_module("content/upload_to_confluence.py")
    assert mod._inline("`code`") == "<code>code</code>"


def test_inline_link(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod._inline("[text](https://example.com)")
    assert result == '<a href="https://example.com">text</a>'


def test_inline_mixed(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod._inline("**bold** and *italic* and `code`")
    assert "<strong>bold</strong>" in result
    assert "<em>italic</em>" in result
    assert "<code>code</code>" in result


def test_heading_conversion(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("# Title")
    assert "<h1>Title</h1>" in result


def test_heading_levels(load_module):
    mod = load_module("content/upload_to_confluence.py")
    for level in range(1, 7):
        hashes = "#" * level
        result = mod.markdown_to_confluence(f"{hashes} Heading {level}")
        assert f"<h{level}>Heading {level}</h{level}>" in result


def test_paragraph(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("Just a paragraph.")
    assert "<p>Just a paragraph.</p>" in result


def test_bullet_list(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("- item 1\n- item 2\n- item 3")
    assert "<ul>" in result
    assert "<li>item 1</li>" in result
    assert "<li>item 2</li>" in result
    assert "<li>item 3</li>" in result
    assert "</ul>" in result


def test_numbered_list(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("1. first\n2. second")
    assert "<ol>" in result
    assert "<li>first</li>" in result
    assert "<li>second</li>" in result


def test_code_block(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("```python\nprint('hello')\n```")
    assert 'ac:name="code"' in result
    assert 'ac:name="language">python' in result
    assert "print('hello')" in result


def test_code_block_no_language(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("```\ncode here\n```")
    assert 'ac:name="language">none' in result


def test_blockquote(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("> This is a quote")
    assert "<blockquote>" in result
    assert "This is a quote" in result


def test_horizontal_rule(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("---")
    assert "<hr/>" in result


def test_checkbox_checked(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("- [x] Done task")
    assert "(/) Done task" in result


def test_checkbox_unchecked(load_module):
    mod = load_module("content/upload_to_confluence.py")
    result = mod.markdown_to_confluence("- [ ] Open task")
    assert "(x) Open task" in result


def test_table_conversion(load_module):
    mod = load_module("content/upload_to_confluence.py")
    md = "| Name | Role |\n|------|------|\n| Alice | PM |\n| Bob | Dev |"
    result = mod.markdown_to_confluence(md)
    assert "<table>" in result
    assert "<th>Name</th>" in result
    assert "<th>Role</th>" in result
    assert "<td>Alice</td>" in result
    assert "<td>Bob</td>" in result


def test_convert_table_skips_separator(load_module):
    mod = load_module("content/upload_to_confluence.py")
    lines = ["| A | B |", "|---|---|", "| 1 | 2 |"]
    result = mod.convert_table(lines)
    assert "<th>A</th>" in result
    assert "<td>1</td>" in result
    # Separator row should not produce a table row
    assert result.count("<tr>") == 2


def test_convert_table_empty(load_module):
    mod = load_module("content/upload_to_confluence.py")
    assert mod.convert_table([]) == ""


def test_full_document(load_module):
    mod = load_module("content/upload_to_confluence.py")
    md = """# My Document

This is a **bold** paragraph with a [link](https://example.com).

## Section 1

- Item A
- Item B

> Important note

```bash
echo hello
```

---

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    result = mod.markdown_to_confluence(md)
    assert "<h1>My Document</h1>" in result
    assert "<strong>bold</strong>" in result
    assert '<a href="https://example.com">link</a>' in result
    assert "<h2>Section 1</h2>" in result
    assert "<ul>" in result
    assert "<blockquote>" in result
    assert 'ac:name="code"' in result
    assert "<hr/>" in result
    assert "<table>" in result
