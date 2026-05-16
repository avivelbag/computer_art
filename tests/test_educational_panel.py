"""Tests for the shared GalleryPanel educational bottom-drawer (lib/panel.js + lib/panel.css).

Covers:
- File existence for lib/panel.js and lib/panel.css
- Required CSS classes and JS API surface
- sessionStorage persistence wiring
- Correct integration in pieces 216, 218, 219 (lib includes + GalleryPanel.init calls)
- Edge cases: empty sections, missing title default, unrelated pieces untouched
- Failure modes: missing class, missing attribute
"""
import pathlib
import re

REPO = pathlib.Path(__file__).parent.parent

PANEL_JS  = REPO / "lib" / "panel.js"
PANEL_CSS = REPO / "lib" / "panel.css"

PIECE_216 = REPO / "pieces" / "216-double-slit" / "index.html"
PIECE_218 = REPO / "pieces" / "218-sir-epidemic" / "index.html"
PIECE_219 = REPO / "pieces" / "219-ising-model" / "index.html"

# A piece that predates the panel and must be unaffected
PIECE_212 = REPO / "pieces" / "212-game-of-life" / "index.html"


# ---------------------------------------------------------------------------
# lib/ file existence
# ---------------------------------------------------------------------------

def test_panel_js_exists():
    """lib/panel.js must exist at repo root level."""
    assert PANEL_JS.is_file(), f"lib/panel.js not found at {PANEL_JS}"


def test_panel_css_exists():
    """lib/panel.css must exist at repo root level."""
    assert PANEL_CSS.is_file(), f"lib/panel.css not found at {PANEL_CSS}"


# ---------------------------------------------------------------------------
# lib/panel.css — required CSS classes and behaviour
# ---------------------------------------------------------------------------

def _css():
    """Return panel.css contents as a string."""
    return PANEL_CSS.read_text(encoding="utf-8")


def test_css_has_gallery_panel_host():
    """Host wrapper class must be defined."""
    assert ".gallery-panel-host" in _css()


def test_css_has_panel_handle():
    """.panel-handle must be defined (the always-visible tab bar)."""
    assert ".panel-handle" in _css()


def test_css_has_panel_drawer():
    """.panel-drawer must be defined (the collapsible content area)."""
    assert ".panel-drawer" in _css()


def test_css_handle_is_fixed_bottom():
    """Host must be pinned to the bottom of the viewport."""
    css = _css()
    assert "position: fixed" in css
    assert "bottom: 0" in css


def test_css_drawer_uses_transform_transition():
    """Drawer must animate with a CSS transform transition."""
    css = _css()
    assert "transform:" in css
    assert "transition:" in css
    assert "translateY" in css


def test_css_open_state_class():
    """Open state must be driven by an .open class on the host."""
    assert ".gallery-panel-host.open" in _css()


def test_css_drawer_max_height_set():
    """Drawer must have a max-height to prevent covering the full viewport."""
    assert "max-height" in _css()


def test_css_mobile_media_query():
    """CSS must include a narrow-screen media query for mobile layouts."""
    assert "@media" in _css()


def test_css_light_theme_overrides():
    """Light-theme overrides must be present (keyed off data-theme attribute)."""
    css = _css()
    assert '[data-theme="light"]' in css


def test_css_chevron_class():
    """.panel-chevron must exist for the open/closed direction indicator."""
    assert ".panel-chevron" in _css()


def test_css_chevron_flips_when_open():
    """Chevron must rotate when panel is open."""
    css = _css()
    assert ".gallery-panel-host.open .panel-chevron" in css
    assert "rotate(180deg)" in css


# ---------------------------------------------------------------------------
# lib/panel.js — API and behaviour
# ---------------------------------------------------------------------------

def _js():
    """Return panel.js contents as a string."""
    return PANEL_JS.read_text(encoding="utf-8")


def test_js_defines_gallery_panel():
    """GalleryPanel must be a top-level const or var."""
    assert "GalleryPanel" in _js()


def test_js_has_init_function():
    """GalleryPanel.init must be exposed."""
    js = _js()
    assert "function init(" in js or "init(" in js


def test_js_returns_init():
    """The module must return { init } so callers can do GalleryPanel.init(...)."""
    assert "return { init }" in _js() or "return {init}" in _js()


def test_js_creates_host_element():
    """JS must create the host DOM element."""
    assert "gallery-panel-host" in _js()


def test_js_creates_handle_element():
    """JS must create the handle DOM element."""
    assert "panel-handle" in _js()


def test_js_creates_drawer_element():
    """JS must create the drawer DOM element."""
    assert "panel-drawer" in _js()


def test_js_session_storage_persistence():
    """Open/closed state must be written to sessionStorage."""
    js = _js()
    assert "sessionStorage" in js
    assert "setItem" in js
    assert "getItem" in js


def test_js_session_storage_key():
    """A named key must be used for sessionStorage to avoid collisions."""
    assert "gallery-panel-open" in _js()


def test_js_aria_expanded():
    """aria-expanded must be toggled for accessibility."""
    assert "aria-expanded" in _js()


def test_js_keyboard_support():
    """Enter and Space keys must activate the handle (accessibility)."""
    js = _js()
    assert "'Enter'" in js or '"Enter"' in js
    assert "' '" in js or '" "' in js or "Space" in js or "e.key === ' '" in js


def test_js_appends_to_body():
    """Panel must be appended to document.body so it lives outside any wrapper."""
    assert "document.body.appendChild" in _js()


def test_js_sections_loop():
    """JS must iterate over the sections array to build the drawer content."""
    js = _js()
    assert "for " in js and "sections" in js


def test_js_default_title():
    """A default title must be provided if the caller omits it."""
    assert "How it works" in _js()


# ---------------------------------------------------------------------------
# Piece 216-double-slit integration
# ---------------------------------------------------------------------------

def _html_216():
    return PIECE_216.read_text(encoding="utf-8")


def test_216_includes_panel_css():
    """Piece 216 must link to ../../lib/panel.css."""
    assert "../../lib/panel.css" in _html_216()


def test_216_includes_panel_js():
    """Piece 216 must load ../../lib/panel.js."""
    assert "../../lib/panel.js" in _html_216()


def test_216_calls_gallery_panel_init():
    """Piece 216 must call GalleryPanel.init({...})."""
    assert "GalleryPanel.init(" in _html_216()


def test_216_panel_has_three_sections():
    """Piece 216 panel must supply at least 3 content sections."""
    html = _html_216()
    count = html.count("heading:")
    assert count >= 3, f"Expected >= 3 sections, found {count}"


def test_216_panel_mentions_slits():
    """Piece 216 'Try this' section must reference the slit controls."""
    html = _html_216()
    assert "slit" in html.lower() or "d-sep" in html or "fringes" in html.lower()


def test_216_panel_js_loaded_before_init():
    """panel.js script tag must appear before the GalleryPanel.init() call."""
    html = _html_216()
    js_pos   = html.index("lib/panel.js")
    init_pos = html.index("GalleryPanel.init(")
    assert js_pos < init_pos, "panel.js must be loaded before GalleryPanel.init is called"


# ---------------------------------------------------------------------------
# Piece 218-sir-epidemic integration
# ---------------------------------------------------------------------------

def _html_218():
    return PIECE_218.read_text(encoding="utf-8")


def test_218_includes_panel_css():
    """Piece 218 must link to ../../lib/panel.css."""
    assert "../../lib/panel.css" in _html_218()


def test_218_includes_panel_js():
    """Piece 218 must load ../../lib/panel.js."""
    assert "../../lib/panel.js" in _html_218()


def test_218_calls_gallery_panel_init():
    """Piece 218 must call GalleryPanel.init({...})."""
    assert "GalleryPanel.init(" in _html_218()


def test_218_panel_has_three_sections():
    """Piece 218 panel must supply at least 3 content sections."""
    html = _html_218()
    count = html.count("heading:")
    assert count >= 3, f"Expected >= 3 sections, found {count}"


def test_218_panel_mentions_r0():
    """Piece 218 panel must mention R₀ (the reproduction number)."""
    html = _html_218()
    assert "R₀" in html or "R₀" in html or "R0" in html


def test_218_panel_js_loaded_before_init():
    """panel.js script tag must appear before the GalleryPanel.init() call."""
    html = _html_218()
    js_pos   = html.index("lib/panel.js")
    init_pos = html.index("GalleryPanel.init(")
    assert js_pos < init_pos, "panel.js must be loaded before GalleryPanel.init is called"


# ---------------------------------------------------------------------------
# Piece 219-ising-model integration
# ---------------------------------------------------------------------------

def _html_219():
    return PIECE_219.read_text(encoding="utf-8")


def test_219_includes_panel_css():
    """Piece 219 must link to ../../lib/panel.css."""
    assert "../../lib/panel.css" in _html_219()


def test_219_includes_panel_js():
    """Piece 219 must load ../../lib/panel.js."""
    assert "../../lib/panel.js" in _html_219()


def test_219_calls_gallery_panel_init():
    """Piece 219 must call GalleryPanel.init({...})."""
    assert "GalleryPanel.init(" in _html_219()


def test_219_panel_has_three_sections():
    """Piece 219 panel must supply at least 3 content sections."""
    html = _html_219()
    count = html.count("heading:")
    assert count >= 3, f"Expected >= 3 sections, found {count}"


def test_219_panel_mentions_temperature():
    """Piece 219 panel must mention temperature or Tc."""
    html = _html_219()
    assert "temperature" in html.lower() or "Tc" in html or "T_c" in html


def test_219_panel_js_loaded_before_init():
    """panel.js script tag must appear before the GalleryPanel.init() call."""
    html = _html_219()
    js_pos   = html.index("lib/panel.js")
    init_pos = html.index("GalleryPanel.init(")
    assert js_pos < init_pos, "panel.js must be loaded before GalleryPanel.init is called"


# ---------------------------------------------------------------------------
# Regression: unrelated pieces must be unaffected
# ---------------------------------------------------------------------------

def test_unrelated_piece_no_panel_css():
    """Piece 212 (Game of Life) must not reference lib/panel.css."""
    if not PIECE_212.is_file():
        return  # piece doesn't exist in this tree — skip
    assert "lib/panel.css" not in PIECE_212.read_text(encoding="utf-8")


def test_unrelated_piece_no_gallery_panel_init():
    """Piece 212 (Game of Life) must not call GalleryPanel.init."""
    if not PIECE_212.is_file():
        return
    assert "GalleryPanel.init" not in PIECE_212.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Edge-case and failure-mode tests (pure logic, no DOM needed)
# ---------------------------------------------------------------------------

class TestPanelJsEdgeCases:
    """Verify edge-case behaviour described in the JS docstring."""

    def test_default_title_fallback_present(self):
        """JS must provide a default value for the title parameter."""
        js = _js()
        assert "How it works" in js, "Default title 'How it works' must be in panel.js"

    def test_sections_empty_array_default(self):
        """JS must default sections to an empty array so init() with no args is safe."""
        js = _js()
        assert "sections = []" in js or "sections=[]" in js

    def test_storage_key_is_string_literal(self):
        """STORAGE_KEY must be a hard-coded string, not a variable from outside."""
        js = _js()
        assert "'gallery-panel-open'" in js or '"gallery-panel-open"' in js

    def test_no_global_leak(self):
        """GalleryPanel must be wrapped in an IIFE or module to avoid global pollution."""
        js = _js()
        assert "(() =>" in js or "(function()" in js, \
            "panel.js must use an IIFE to encapsulate its internals"


class TestPanelCssFailureModes:
    """Verify that required structural properties are present."""

    def test_drawer_transform_starts_hidden(self):
        """Closed state must use translateY(100%) to hide the drawer."""
        css = _css()
        assert "translateY(100%)" in css

    def test_open_state_uses_translate_zero(self):
        """Open state must reset the transform to translateY(0)."""
        css = _css()
        assert "translateY(0)" in css

    def test_drawer_overflow_scroll(self):
        """Drawer must allow scrolling when its content overflows."""
        css = _css()
        assert "overflow-y: auto" in css or "overflow-y:auto" in css

    def test_handle_has_cursor_pointer(self):
        """Handle must show a pointer cursor to signal it is clickable."""
        assert "cursor: pointer" in _css()

    def test_missing_open_class_means_hidden(self):
        """Without .open on the host, the drawer must remain translated away."""
        css = _css()
        # Verify the closed state rule (.panel-drawer alone, not .open .panel-drawer)
        # is the translateY(100%) rule
        closed_match = re.search(
            r'\.panel-drawer\s*\{[^}]*translateY\(100%\)', css, re.DOTALL
        )
        assert closed_match, ".panel-drawer default transform must be translateY(100%)"
