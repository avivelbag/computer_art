/**
 * GalleryPanel — shared reusable educational bottom-drawer.
 *
 * Usage (call once at the bottom of each piece's <script>):
 *
 *   GalleryPanel.init({
 *     title: "How it works",
 *     sections: [
 *       { heading: "The physics", body: "…" },
 *       { heading: "Key concepts", body: "…" },
 *       { heading: "Try this",    body: "…" },
 *     ]
 *   });
 *
 * Open/closed state is persisted in sessionStorage under the key
 * 'gallery-panel-open', so a soft reload (F5) remembers the user's choice.
 *
 * Requires lib/panel.css to be loaded first.
 */
const GalleryPanel = (() => {
  const STORAGE_KEY = 'gallery-panel-open';

  /**
   * Build and attach the bottom-drawer panel to document.body.
   *
   * @param {Object} opts
   * @param {string} opts.title    - Label shown on the handle tab and as the
   *                                 heading inside the drawer.
   * @param {Array<{heading:string, body:string}>} opts.sections
   *                               - Content sections rendered inside the drawer.
   *                                 Each entry creates an <h3> + <p> pair.
   */
  function init({ title = 'How it works', sections = [] } = {}) {
    const host = document.createElement('div');
    host.className = 'gallery-panel-host';

    /* --- Drawer ----------------------------------------------------------------
     * Absolutely positioned above the handle (bottom: 100%). Starts translated
     * down by its own height (hidden); slides to translateY(0) when open.
     */
    const drawer = document.createElement('div');
    drawer.className = 'panel-drawer';
    drawer.setAttribute('aria-hidden', 'true');

    const inner = document.createElement('div');
    inner.className = 'panel-drawer-inner';

    const titleEl = document.createElement('div');
    titleEl.className = 'panel-drawer-title';
    titleEl.textContent = title;
    inner.appendChild(titleEl);

    for (const sec of sections) {
      const sectionEl = document.createElement('div');
      sectionEl.className = 'panel-section';

      const h3 = document.createElement('h3');
      h3.textContent = sec.heading;

      const p = document.createElement('p');
      p.textContent = sec.body;

      sectionEl.appendChild(h3);
      sectionEl.appendChild(p);
      inner.appendChild(sectionEl);
    }

    drawer.appendChild(inner);

    /* --- Handle ---------------------------------------------------------------
     * Always visible at the bottom of the viewport. Clicking toggles the drawer.
     */
    const handle = document.createElement('div');
    handle.className = 'panel-handle';
    handle.setAttribute('role', 'button');
    handle.setAttribute('tabindex', '0');
    handle.setAttribute('aria-expanded', 'false');
    handle.setAttribute('aria-label', 'Toggle educational panel');

    const chevron = document.createElement('span');
    chevron.className = 'panel-chevron';
    chevron.setAttribute('aria-hidden', 'true');
    chevron.textContent = '▲'; /* ▲ */

    const labelSpan = document.createElement('span');
    labelSpan.textContent = title;

    handle.appendChild(chevron);
    handle.appendChild(labelSpan);

    /* Drawer before handle so it stacks above (flex column from top to bottom,
     * but the drawer is absolute so layout order doesn't matter for the handle). */
    host.appendChild(drawer);
    host.appendChild(handle);
    document.body.appendChild(host);

    /* --- Restore persisted state ---------------------------------------------- */
    const wasOpen = sessionStorage.getItem(STORAGE_KEY) === 'true';
    if (wasOpen) {
      host.classList.add('open');
      handle.setAttribute('aria-expanded', 'true');
      drawer.setAttribute('aria-hidden', 'false');
    }

    /**
     * Toggle the drawer open/closed and persist the new state to sessionStorage.
     */
    function toggle() {
      const nowOpen = host.classList.toggle('open');
      sessionStorage.setItem(STORAGE_KEY, String(nowOpen));
      handle.setAttribute('aria-expanded', String(nowOpen));
      drawer.setAttribute('aria-hidden', String(!nowOpen));
    }

    handle.addEventListener('click', toggle);

    /* Keyboard accessibility: Enter or Space activate the handle. */
    handle.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggle();
      }
    });
  }

  return { init };
})();
