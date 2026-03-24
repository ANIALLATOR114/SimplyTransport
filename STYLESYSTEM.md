# SimplyTransport style system

This document explains how the style system (css) is built.

## Goals

- **Vanilla CSS** — no Tailwind, PostCSS pipeline, or component framework.
- **One global fetch** — `[SimplyTransport/templates/base.html](SimplyTransport/templates/base.html)` loads a single `[SimplyTransport/static/static/style.css](SimplyTransport/static/static/style.css)` with a `?version` query (same value as the OpenAPI app version) for cache busting.
- **Optional page CSS** — `[delays.css](SimplyTransport/static/static/delays.css)` and `[event.css](SimplyTransport/static/static/event.css)` are linked only from templates that need them.

## File layout


| File         | Role                                                                                                              |
| ------------ | ----------------------------------------------------------------------------------------------------------------- |
| `style.css`  | Tokens, `@layer` structure, layout, navbar, tables, maps (Leaflet), responsive rules. |
| `delays.css` | Delays-specific UI (e.g. expand rows).                                                                            |
| `event.css`  | Events page tweaks.                                                                                               |
| `fonts.html` | Self-hosted Roboto `@font-face` (included from `base.html`).                                                      |


Global styles live in **one** `style.css` file, grouped with **section comments** (e.g. `/* === tokens / :root === */`, `/* === components: navbar === */`, `/* === maps: Leaflet === */`).

## Design tokens (`:root`)

Semantic colors include:

- `--bg-color`, `--bg-color-bump`, `--bg-color-bump-border`, `--bg-color-bump-even`, `--bg-color-highlight`, `--bg-color-light`
- `--font-color`, `--font-color-secondary`, `--font-color-highlight`, `--font-color-highlight-light`
- Aliases: `--surface-0`, `--surface-1`, `--border-subtle` (map to the bump palette)
- Spacing: `--space-1` … `--space-4`; radius: `--radius-sm`, `--radius-md`; shadow: `--shadow-sm`

Avoid `!important` on tokens unless unavoidable; prefer **layers** and specificity.

## Cascade layers (`@layer`)

After `:root`, `style.css` declares `@layer base, components, utilities` and groups rules into:


| Layer        | Contents                                                                                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `base`       | Universal selector, scrollbars, `body`, headings, `.dense-text`, `.container` / `.narrow-container`, page shell (`.page-container`, `.content-wrap`), footer strip |
| `components` | Tables, cards, navbar, Leaflet, loaders, realtime widgets, `@keyframes`, responsive `@media` blocks                                                                |
| `utilities`  | Helpers (`.no-top-margin`, `.bottom-margin`, `.bullet-points`, etc.)                                                                                               |


**Unlayered** rules (only `:root` here) win over layered rules at equal specificity. Within layers, **later** layers override earlier ones when specificity ties. Prefer that ordering over `!important` on design tokens.

If styles ever look “missing” after a CSS change, hard-refresh the browser—**stale cache** can show an old bundle; cascade layers themselves are [widely supported](https://caniuse.com/css-cascade-layers) in current browsers.

## Maps (Leaflet / Folium)

Alternate **tile layers** are not used (performance/cost). The app keeps OSM (or your existing) tiles and blends the UI with:

- A subtle `filter` on `.leaflet-container`
- Themed `.leaflet-bar`, `.leaflet-control-layers`, `.leaflet-control-attribution` (Leaflet’s defaults often need `!important` to override)

## Charts (Lightweight Charts)

Trip delay charts are configured in `[SimplyTransport/templates/widgets/delays_specific.html](SimplyTransport/templates/widgets/delays_specific.html)`: layout background and grid colors align with `--surface-1` / accent purple. The graph host uses `.delays-chart-container` in `style.css`.

## Typography

Roboto only.

## Evolving safely

1. **New global rule** → add under the right **section comment** and `**@layer`**.
2. **New token** → add to `:root`, reuse via `var(...)`.
3. **New page-only styles** → small optional CSS file + `<link>` in that template, or a section in `style.css` if it’s shared.
4. After structural changes, update this file.

