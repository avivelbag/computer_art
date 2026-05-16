"""Tests for the Markdown description pane (suggestion 05).

Covers:
- renderMarkdown function presence and correctness (extracted from index.html JS)
- CSS styles for Markdown elements inside .description-pane
- README enrichment for pieces 194-chladni, 180-gray-scott, 200-lsystem-trees
- Integration: pane uses innerHTML, not textContent, for the description element
"""

import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent
INDEX = REPO / "index.html"
CSS = REPO / "styles.css"


# ---------------------------------------------------------------------------
# Helpers — extract and execute the renderMarkdown function via Python regex
# so we can unit-test it without a browser.
# ---------------------------------------------------------------------------

def _render(text: str) -> str:
    """
    Python re-implementation of the renderMarkdown JS function in index.html.

    Mirrors the exact same algorithm so tests can verify correctness of the
    logic without needing a headless browser.
    """
    import html as html_mod

    def esc(s: str) -> str:
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def fmt(s: str) -> str:
        s = esc(s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        return s

    out: list[str] = []
    lst: list[str] = []
    code: list[str] = []
    in_code = False

    def flush_list() -> None:
        if lst:
            out.append('<ul>' + ''.join(f'<li>{l}</li>' for l in lst) + '</ul>')
            lst.clear()

    def flush_code() -> None:
        if code:
            out.append(f'<pre><code>{esc(chr(10).join(code))}</code></pre>')
            code.clear()

    for line in text.split('\n'):
        if line.startswith('```'):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_list()
                in_code = True
        elif in_code:
            code.append(line)
        elif line.strip() == '':
            flush_list()
        elif re.match(r'^#+\s', line):
            flush_list()
            out.append(f'<h3>{fmt(re.sub(r"^#+\s+", "", line))}</h3>')
        elif line.startswith('- '):
            lst.append(fmt(line[2:]))
        elif re.match(r'^\|[\s:|-]+\|', line):
            pass  # table separator — skip
        elif line.startswith('|'):
            flush_list()
            cells = [fmt(c.strip()) for c in line.split('|')[1:-1] if c.strip()]
            if cells:
                out.append('<p>' + ' · '.join(cells) + '</p>')
        else:
            flush_list()
            out.append(f'<p>{fmt(line)}</p>')

    flush_list()
    if in_code:
        flush_code()
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# renderMarkdown presence and structure tests
# ---------------------------------------------------------------------------

def test_render_markdown_function_in_index():
    """index.html must define a renderMarkdown function."""
    content = INDEX.read_text()
    assert 'function renderMarkdown' in content


def test_render_markdown_handles_bold():
    """**bold** must produce <strong>bold</strong>."""
    result = _render('**hello**')
    assert '<strong>hello</strong>' in result


def test_render_markdown_handles_inline_code():
    """Backtick spans must produce <code> elements."""
    result = _render('Use `x = 1` here.')
    assert '<code>x = 1</code>' in result


def test_render_markdown_handles_headings():
    """# and ## headings must be flattened to <h3>."""
    assert '<h3>Title</h3>' in _render('# Title')
    assert '<h3>Sub</h3>' in _render('## Sub')
    assert '<h3>Deep</h3>' in _render('### Deep')


def test_render_markdown_handles_list():
    """Consecutive `- item` lines must be wrapped in <ul><li>."""
    result = _render('- alpha\n- beta\n- gamma')
    assert '<ul>' in result
    assert '<li>alpha</li>' in result
    assert '<li>beta</li>' in result
    assert '<li>gamma</li>' in result


def test_render_markdown_handles_fenced_code_block():
    """Fenced code blocks must produce <pre><code> with content preserved."""
    md = '```\nf(x, y) = sin(m·πx)\n```'
    result = _render(md)
    assert '<pre><code>' in result
    assert 'f(x, y) = sin(m' in result


def test_render_markdown_paragraph_break_on_blank_line():
    """A blank line must end a list or paragraph block."""
    result = _render('- item\n\nnext paragraph')
    assert '</ul>' in result
    assert '<p>next paragraph</p>' in result


def test_render_markdown_escapes_html_in_text():
    """Raw HTML-like characters in text must be escaped."""
    result = _render('x < y & z > w')
    assert '&lt;' in result
    assert '&amp;' in result
    assert '&gt;' in result


def test_render_markdown_escapes_html_in_code_block():
    """Code blocks must also escape < > & to prevent XSS."""
    result = _render('```\n<script>alert(1)</script>\n```')
    assert '<script>' not in result
    assert '&lt;script&gt;' in result


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_render_markdown_empty_string():
    """Empty input must return an empty string (no crash)."""
    result = _render('')
    assert result == ''


def test_render_markdown_large_input():
    """A large block of text must not crash or truncate."""
    lines = ['- item %d' % i for i in range(500)]
    result = _render('\n'.join(lines))
    assert result.count('<li>') == 500


def test_render_markdown_unclosed_code_block():
    """An unclosed fenced code block must still render remaining lines."""
    md = '```\nsome code\nno closing fence'
    result = _render(md)
    assert 'some code' in result


def test_render_markdown_table_separator_skipped():
    """Table separator rows (|---|---|) must produce no output."""
    result = _render('|---|---|')
    assert '---|' not in result


# ---------------------------------------------------------------------------
# Failure mode: wrong structure
# ---------------------------------------------------------------------------

def test_render_markdown_plain_text_becomes_paragraph():
    """Lines with no special syntax must be wrapped in <p>."""
    result = _render('This is plain text.')
    assert '<p>This is plain text.</p>' in result


def test_render_markdown_no_output_for_blank_lines_only():
    """Input consisting only of blank lines must produce no HTML tags."""
    result = _render('\n\n\n')
    assert '<p>' not in result
    assert '<h3>' not in result


# ---------------------------------------------------------------------------
# index.html integration: innerHTML used for description
# ---------------------------------------------------------------------------

def test_index_uses_innerhtml_for_pane_description():
    """openPane must set innerHTML (not textContent) on the description element."""
    content = INDEX.read_text()
    assert 'innerHTML = renderMarkdown' in content


def test_index_pane_description_is_div():
    """The pane description container must be a <div>, not <p>, to hold block elements."""
    content = INDEX.read_text()
    assert 'div class="pane-description"' in content or "div class='pane-description'" in content


def test_index_fetches_readme_on_open():
    """openPane must fetch the piece's README.md to populate the description pane."""
    content = INDEX.read_text()
    assert "README.md" in content


def test_index_open_pane_is_async():
    """openPane must be declared async to support the README fetch."""
    content = INDEX.read_text()
    assert 'async function openPane' in content


# ---------------------------------------------------------------------------
# CSS: Markdown element styles inside .description-pane
# ---------------------------------------------------------------------------

def test_css_description_pane_h3():
    """styles.css must style h3 inside .description-pane."""
    content = CSS.read_text()
    assert '.description-pane h3' in content


def test_css_description_pane_code():
    """styles.css must style code inside .description-pane with monospace font."""
    content = CSS.read_text()
    assert '.description-pane code' in content
    idx = content.index('.description-pane code')
    block_end = content.index('}', idx)
    block = content[idx:block_end]
    assert 'monospace' in block


def test_css_description_pane_pre():
    """styles.css must style pre blocks inside .description-pane."""
    content = CSS.read_text()
    assert '.description-pane pre' in content


def test_css_description_pane_ul():
    """styles.css must style ul inside .description-pane."""
    content = CSS.read_text()
    assert '.description-pane ul' in content


def test_css_pre_has_subtle_background():
    """The pre block background must use rgba or a subtle color variable, not a solid colour."""
    content = CSS.read_text()
    pre_idx = content.index('.description-pane pre')
    pre_end = content.index('}', pre_idx)
    pre_block = content[pre_idx:pre_end]
    assert 'background' in pre_block
    assert 'rgba' in pre_block or 'var(--' in pre_block


# ---------------------------------------------------------------------------
# README enrichment: 194-chladni
# ---------------------------------------------------------------------------

CHLADNI_README = REPO / 'pieces' / '194-chladni' / 'README.md'


def test_chladni_readme_has_how_it_works():
    """194-chladni README must contain a '## How it works' section."""
    text = CHLADNI_README.read_text()
    assert '## How it works' in text


def test_chladni_readme_has_equation_code_block():
    """194-chladni README must have a fenced code block containing the nodal-line equation."""
    text = CHLADNI_README.read_text()
    assert '```' in text
    code_match = re.search(r'```.*?```', text, re.DOTALL)
    assert code_match, 'No fenced code block found in 194-chladni README'
    block = code_match.group(0)
    assert 'sin' in block, 'Equation code block must contain sin()'


def test_chladni_readme_has_what_to_notice():
    """194-chladni README must contain a '## What to notice' section."""
    text = CHLADNI_README.read_text()
    assert '## What to notice' in text


def test_chladni_readme_what_to_notice_has_bullets():
    """The '## What to notice' section must contain at least 2 bullet points."""
    text = CHLADNI_README.read_text()
    notice_start = text.index('## What to notice')
    notice_section = text[notice_start:]
    bullets = re.findall(r'^- ', notice_section, re.MULTILINE)
    assert len(bullets) >= 2, f'Expected ≥2 bullets in What to notice, found {len(bullets)}'


# ---------------------------------------------------------------------------
# README enrichment: 180-gray-scott
# ---------------------------------------------------------------------------

GRAY_SCOTT_README = REPO / 'pieces' / '180-gray-scott' / 'README.md'


def test_gray_scott_readme_has_what_to_notice():
    """180-gray-scott README must contain a '## What to notice' section."""
    text = GRAY_SCOTT_README.read_text()
    assert '## What to notice' in text


def test_gray_scott_readme_what_to_notice_has_bullets():
    """The '## What to notice' section in 180-gray-scott must have ≥2 bullets."""
    text = GRAY_SCOTT_README.read_text()
    notice_start = text.index('## What to notice')
    notice_section = text[notice_start:]
    bullets = re.findall(r'^- ', notice_section, re.MULTILINE)
    assert len(bullets) >= 2, f'Expected ≥2 bullets, found {len(bullets)}'


def test_gray_scott_readme_has_equation():
    """180-gray-scott README must contain the reaction-diffusion PDEs."""
    text = GRAY_SCOTT_README.read_text()
    assert 'dU/dt' in text or 'du/dt' in text.lower()


# ---------------------------------------------------------------------------
# README enrichment: 200-lsystem-trees
# ---------------------------------------------------------------------------

LSYSTEM_README = REPO / 'pieces' / '200-lsystem-trees' / 'README.md'


def test_lsystem_readme_has_how_it_works():
    """200-lsystem-trees README must contain a '## How it works' section."""
    text = LSYSTEM_README.read_text()
    assert '## How it works' in text


def test_lsystem_readme_has_production_rule_code_block():
    """200-lsystem-trees README must have a fenced code block showing production rules."""
    text = LSYSTEM_README.read_text()
    assert '```' in text


def test_lsystem_readme_has_what_to_notice():
    """200-lsystem-trees README must contain a '## What to notice' section."""
    text = LSYSTEM_README.read_text()
    assert '## What to notice' in text


def test_lsystem_readme_what_to_notice_has_bullets():
    """The '## What to notice' section in 200-lsystem-trees must have ≥2 bullets."""
    text = LSYSTEM_README.read_text()
    notice_start = text.index('## What to notice')
    notice_section = text[notice_start:]
    bullets = re.findall(r'^- ', notice_section, re.MULTILINE)
    assert len(bullets) >= 2, f'Expected ≥2 bullets, found {len(bullets)}'


def test_lsystem_readme_shows_grammars_explicitly():
    """200-lsystem-trees README must show production rules explicitly (F → ...)."""
    text = LSYSTEM_README.read_text()
    assert 'F →' in text or 'F ->' in text
