import pathlib

REPO = pathlib.Path(__file__).parent.parent
INDEX = REPO / "index.html"
CSS = REPO / "styles.css"

THEME_KEY = "theme"


def test_index_exists():
    assert INDEX.exists()


def test_theme_toggle_button_present():
    content = INDEX.read_text()
    assert 'id="theme-toggle"' in content


def test_localstorage_key_consistent():
    """The theme localStorage key must be 'theme' and appear in index.html."""
    content = INDEX.read_text()
    assert "localStorage" in content
    assert f"'{THEME_KEY}'" in content or f'"{THEME_KEY}"' in content


def test_keydown_handler_present():
    content = INDEX.read_text()
    assert "keydown" in content


def test_css_dark_theme_selector():
    content = CSS.read_text()
    assert '[data-theme="dark"]' in content


def test_css_light_mode_variables():
    content = CSS.read_text()
    assert "--bg:" in content
    assert "--text:" in content
    assert "--card-bg:" in content


def test_arrow_key_navigation_present():
    content = INDEX.read_text()
    assert "ArrowRight" in content
    assert "ArrowLeft" in content


def test_escape_key_present():
    content = INDEX.read_text()
    assert "Escape" in content


def test_focus_ring_in_css():
    content = CSS.read_text()
    assert ".card:focus" in content


def test_theme_toggle_aria_label():
    content = INDEX.read_text()
    idx = content.index('id="theme-toggle"')
    surrounding = content[max(0, idx - 120):idx + 120]
    assert "aria-label" in surrounding


class TestEdgeCases:
    def test_index_html_is_valid_utf8(self):
        INDEX.read_bytes().decode("utf-8")

    def test_css_root_has_bg_variable(self):
        content = CSS.read_text()
        root_start = content.index(":root")
        root_end = content.index("}", root_start)
        root_block = content[root_start:root_end]
        assert "--bg:" in root_block

    def test_no_external_dependencies_in_html(self):
        """index.html must not load external scripts or stylesheets."""
        content = INDEX.read_text()
        assert "https://" not in content
        assert "http://" not in content

    def test_localstorage_set_and_get_both_present(self):
        content = INDEX.read_text()
        assert "localStorage.setItem" in content
        assert "localStorage.getItem" in content


class TestFailureModes:
    def test_dark_mode_bg_differs_from_light(self):
        """Dark and light --bg values must be distinct colors."""
        content = CSS.read_text()

        root_start = content.index(":root")
        root_end = content.index("}", root_start)
        root_block = content[root_start:root_end]

        dark_start = content.index('[data-theme="dark"]')
        dark_end = content.index("}", dark_start)
        dark_block = content[dark_start:dark_end]

        def extract_bg(block):
            for line in block.splitlines():
                if "--bg:" in line:
                    return line.split("--bg:")[1].strip().rstrip(";").strip()
            return None

        light_bg = extract_bg(root_block)
        dark_bg = extract_bg(dark_block)
        assert light_bg is not None, "Light mode must define --bg"
        assert dark_bg is not None, "Dark mode must define --bg"
        assert light_bg != dark_bg, "Light and dark --bg must differ"

    def test_card_focus_outline_uses_variable(self):
        """The focus ring should use a CSS variable for theme consistency."""
        content = CSS.read_text()
        focus_start = content.index(".card:focus")
        focus_end = content.index("}", focus_start)
        focus_block = content[focus_start:focus_end]
        assert "var(--" in focus_block

    def test_theme_toggle_not_inside_grid(self):
        """The toggle button must be in the header, not the card grid."""
        content = INDEX.read_text()
        grid_start = content.index('id="grid"')
        toggle_pos = content.index('id="theme-toggle"')
        assert toggle_pos < grid_start, "theme-toggle must appear before #grid"
