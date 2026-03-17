"""Tests for content/upload_to_docs.py — markdown tokenization and Docs API request building."""


def test_tokenise_plain_text(load_module):
    mod = load_module("content/upload_to_docs.py")
    segments = mod._tokenise_inline("hello world")
    assert len(segments) == 1
    assert segments[0]["text"] == "hello world"
    assert "bold" not in segments[0]


def test_tokenise_bold(load_module):
    mod = load_module("content/upload_to_docs.py")
    segments = mod._tokenise_inline("say **bold** word")
    assert len(segments) == 3
    assert segments[0]["text"] == "say "
    assert segments[1]["text"] == "bold"
    assert segments[1]["bold"] is True
    assert segments[2]["text"] == " word"


def test_tokenise_italic(load_module):
    mod = load_module("content/upload_to_docs.py")
    segments = mod._tokenise_inline("an *italic* word")
    assert any(s.get("italic") for s in segments)


def test_tokenise_code(load_module):
    mod = load_module("content/upload_to_docs.py")
    segments = mod._tokenise_inline("use `var` here")
    assert any(s.get("code") for s in segments)
    code_seg = [s for s in segments if s.get("code")][0]
    assert code_seg["text"] == "var"


def test_tokenise_link(load_module):
    mod = load_module("content/upload_to_docs.py")
    segments = mod._tokenise_inline("click [here](https://example.com) now")
    link_seg = [s for s in segments if s.get("link")][0]
    assert link_seg["text"] == "here"
    assert link_seg["link"] == "https://example.com"


def test_tokenise_mixed(load_module):
    mod = load_module("content/upload_to_docs.py")
    segments = mod._tokenise_inline("**bold** and *italic* and `code`")
    bold_segs = [s for s in segments if s.get("bold")]
    italic_segs = [s for s in segments if s.get("italic")]
    code_segs = [s for s in segments if s.get("code")]
    assert len(bold_segs) == 1
    assert len(italic_segs) == 1
    assert len(code_segs) == 1


def test_process_inline_formatting_plain(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs, end_idx = mod.process_inline_formatting("hello", 1)
    assert len(reqs) == 1
    assert reqs[0]["insertText"]["text"] == "hello"
    assert reqs[0]["insertText"]["location"]["index"] == 1
    assert end_idx == 6


def test_process_inline_formatting_bold(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs, _ = mod.process_inline_formatting("**bold**", 1)
    # Should have insertText + updateTextStyle
    insert_reqs = [r for r in reqs if "insertText" in r]
    style_reqs = [r for r in reqs if "updateTextStyle" in r]
    assert len(insert_reqs) == 1
    assert insert_reqs[0]["insertText"]["text"] == "bold"
    assert len(style_reqs) == 1
    assert style_reqs[0]["updateTextStyle"]["textStyle"]["bold"] is True


def test_process_inline_formatting_link(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs, _ = mod.process_inline_formatting("[click](https://example.com)", 1)
    link_reqs = [r for r in reqs if "updateTextStyle" in r and "link" in r.get("updateTextStyle", {}).get("textStyle", {})]
    assert len(link_reqs) == 1
    assert link_reqs[0]["updateTextStyle"]["textStyle"]["link"]["url"] == "https://example.com"


def test_markdown_to_docs_requests_heading(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs = mod.markdown_to_docs_requests("# Hello")
    style_reqs = [r for r in reqs if "updateParagraphStyle" in r]
    assert any(
        r["updateParagraphStyle"]["paragraphStyle"]["namedStyleType"] == "HEADING_1"
        for r in style_reqs
    )


def test_markdown_to_docs_requests_code_block(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs = mod.markdown_to_docs_requests("```\ncode\n```")
    insert_reqs = [r for r in reqs if "insertText" in r]
    assert any("code" in r["insertText"]["text"] for r in insert_reqs)
    # Should have monospace styling
    style_reqs = [r for r in reqs if "updateTextStyle" in r]
    assert any(
        "Courier New" in str(r.get("updateTextStyle", {}).get("textStyle", {}))
        for r in style_reqs
    )


def test_markdown_to_docs_requests_bullet(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs = mod.markdown_to_docs_requests("- item one\n- item two")
    bullet_reqs = [r for r in reqs if "createParagraphBullets" in r]
    assert len(bullet_reqs) == 2


def test_markdown_to_docs_requests_numbered_list(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs = mod.markdown_to_docs_requests("1. first\n2. second")
    bullet_reqs = [r for r in reqs if "createParagraphBullets" in r]
    assert len(bullet_reqs) == 2
    assert bullet_reqs[0]["createParagraphBullets"]["bulletPreset"] == "NUMBERED_DECIMAL_ALPHA_ROMAN"


def test_markdown_to_docs_requests_hr(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs = mod.markdown_to_docs_requests("---")
    style_reqs = [r for r in reqs if "updateParagraphStyle" in r]
    assert any("borderBottom" in str(r) for r in style_reqs)


def test_markdown_to_docs_requests_empty_lines(load_module):
    mod = load_module("content/upload_to_docs.py")
    reqs = mod.markdown_to_docs_requests("line one\n\nline two")
    insert_reqs = [r for r in reqs if "insertText" in r]
    texts = [r["insertText"]["text"] for r in insert_reqs]
    assert any(t == "\n" for t in texts)  # empty line becomes newline
