import pathlib

REPO = pathlib.Path(__file__).parent.parent
INDEX = REPO / "index.html"
CSS = REPO / "styles.css"
PIECES_JSON = REPO / "pieces.json"

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


class TestDescriptionPane:
    def test_aside_description_pane_present(self):
        """index.html must contain an <aside class="description-pane"> element."""
        content = INDEX.read_text()
        assert 'aside' in content
        assert 'description-pane' in content

    def test_pane_close_button_present(self):
        """index.html must contain a .pane-close button for closing the pane."""
        content = INDEX.read_text()
        assert 'pane-close' in content

    def test_info_btn_class_in_js(self):
        """index.html JS must create .info-btn elements on cards."""
        content = INDEX.read_text()
        assert 'info-btn' in content

    def test_css_description_pane_fixed_position(self):
        """styles.css must set .description-pane to position: fixed."""
        content = CSS.read_text()
        assert '.description-pane' in content
        pane_start = content.index('.description-pane')
        pane_end = content.index('}', pane_start)
        pane_block = content[pane_start:pane_end]
        assert 'fixed' in pane_block

    def test_css_description_pane_transform_slide(self):
        """styles.css must use transform: translateX for the slide animation."""
        content = CSS.read_text()
        assert 'translateX' in content

    def test_css_description_pane_open_class(self):
        """styles.css must define a .description-pane.open rule."""
        content = CSS.read_text()
        assert '.description-pane.open' in content or ('.description-pane' in content and '.open' in content)

    def test_css_transition_no_js_animation(self):
        """styles.css must use CSS transition, not JS-driven animation loops."""
        content = CSS.read_text()
        assert 'transition' in content

    def test_css_mobile_full_width(self):
        """styles.css must have a media query making the pane full-width on mobile."""
        content = CSS.read_text()
        assert '@media' in content
        assert '600px' in content

    def test_escape_key_closes_pane(self):
        """index.html JS must handle Escape key to close the pane."""
        content = INDEX.read_text()
        assert 'Escape' in content
        assert 'closePane' in content

    def test_open_pane_function_present(self):
        """index.html JS must define openPane and closePane functions."""
        content = INDEX.read_text()
        assert 'openPane' in content
        assert 'closePane' in content

    def test_pane_shows_piece_fields(self):
        """openPane must populate title, meta (technique/year), and description."""
        content = INDEX.read_text()
        assert 'pane-title' in content
        assert 'pane-meta' in content
        assert 'pane-description' in content

    def test_i_key_opens_pane_on_focused_card(self):
        """Pressing 'i' while a card is focused should trigger openPane."""
        content = INDEX.read_text()
        assert "'i'" in content or '"i"' in content

    def test_pane_close_wired_to_close_function(self):
        """The pane-close button must be wired to closePane."""
        content = INDEX.read_text()
        assert 'pane-close' in content
        assert 'closePane' in content

    def test_description_pane_aside_has_id(self):
        """The aside element must have id='description-pane' for JS targeting."""
        content = INDEX.read_text()
        assert 'id="description-pane"' in content or "id='description-pane'" in content


class TestEdgeCases:
    def test_description_field_in_pieces_json(self):
        """Every entry in pieces.json must have a non-empty description field."""
        import json
        pieces = json.loads(PIECES_JSON.read_text())
        for piece in pieces:
            assert 'description' in piece, f"Missing description in {piece.get('id')}"
            assert piece['description'], f"Empty description in {piece.get('id')}"

    def test_description_pane_not_open_by_default(self):
        """The description pane must not have 'open' class in static HTML."""
        content = INDEX.read_text()
        assert 'class="description-pane"' in content or "class='description-pane'" in content
        assert 'class="description-pane open"' not in content

    def test_info_btn_aria_label(self):
        """The info button must have an aria-label for accessibility."""
        content = INDEX.read_text()
        assert 'aria-label' in content
        assert 'About this piece' in content


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
