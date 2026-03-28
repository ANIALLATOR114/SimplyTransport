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
- Surfaces: `--surface-0`, `--surface-1` (aliases onto the bump palette), plus **`--surface-2`** for raised panels (cards, map controls)
- Borders: `--border-subtle`, **`--border-soft`** (softer edge via `color-mix` with transparent)
- Status (realtime / legend): **`--status-early`**, **`--status-on-time`**, **`--status-late`**, **`--status-unknown`**
- Spacing: `--space-1` … `--space-4`; radius: `--radius-sm`, `--radius-md`; shadows: **`--shadow-sm`**, **`--shadow-md`**
- Motion: **`--transition-fast`**; sticky tables: **`--navbar-sticky-offset`** (desktop; table headers use this so they sit below the sticky navbar). Sticky **`.table-search th`** intentionally omits **`z-index`** so the first body row is not painted under the header; **`border-collapse: separate`** avoids overlap quirks with sticky cells.

`color-mix()` is used for borders and the sticky navbar tint; target evergreen browsers. Avoid `!important` on tokens unless unavoidable; prefer **layers** and specificity.

## Cascade layers (`@layer`)

After `:root`, `style.css` declares `@layer base, components, utilities` and groups rules into:


| Layer        | Contents                                                                                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `base`       | Universal selector, scrollbars, `body`, headings, `.dense-text`, `.container` / `.narrow-container`, page shell (`.page-container`, `.content-wrap`), footer strip |
| `components` | Tables (including sticky headers), cards (`.inner-container`), **`.table-search--static-head`** when `position: sticky` on `th` would misbehave (nested horizontal scroll + `top` offset), **`.search-results-stack`** on `.inner-container` for GTFS stop/route search (search input + results table in one card), navbar (`.navbar`, **`.navbar-segment`** for grouped links), loaders, realtime widgets, `@keyframes`, responsive `@media` blocks                                                                       |
| `utilities`  | Helpers (`.tabular` for tabular numerals, `.no-top-margin`, `.bottom-margin`, `.bullet-points`, etc.)                                                                                               |


**Unlayered** rules (only `:root` here) win over layered rules at equal specificity. Within layers, **later** layers override earlier ones when specificity ties. Prefer that ordering over `!important` on design tokens.

If styles ever look “missing” after a CSS change, hard-refresh the browser—**stale cache** can show an old bundle; cascade layers themselves are [widely supported](https://caniuse.com/css-cascade-layers) in current browsers.

## Maps (MapLibre)

Interactive maps use **MapLibre GL JS** in the main page (no iframe). Shared styling lives under `.map-container--maplibre`, `#map-element`, and `.maplibre-*` popup/tooltip classes in `style.css`. Basemap tiles are OpenStreetMap raster sources.

## Charts (Lightweight Charts)

Trip delay charts are configured in `[SimplyTransport/templates/widgets/delays_specific.html](SimplyTransport/templates/widgets/delays_specific.html)`: layout background and grid colors align with `--surface-1` / accent purple. The graph host uses `.delays-chart-container` in `style.css`.

## Typography

Roboto only.

## Evolving safely

1. **New global rule** → add under the right **section comment** and `**@layer`**.
2. **New token** → add to `:root`, reuse via `var(...)`.
3. **New page-only styles** → small optional CSS file + `<link>` in that template, or a section in `style.css` if it’s shared.
4. After structural changes, update this file.

