# Unified Styling System (Dark/Light Safe)

This document defines the enforceable styling system for NiceGUI + Tailwind + Material Icons.

## Goal

Create a single styling system that:

- works reliably with Dark/Light mode toggling
- avoids hard-coded colors scattered in components
- allows Tailwind layout utilities while preserving a consistent theme
- supports Material Icons usage consistently
- is maintainable and scalable

## Non-Negotiable Rules

1. No hard-coded colors in UI components.
2. Dark/Light must be driven by a single root switch.
3. All custom styling must flow through a centralized design-token layer.
4. Every reusable component must declare which semantic tokens it uses.

## Token-First Theme + Tailwind for Layout

Use CSS variables as design tokens and map Tailwind color utilities to those tokens.

- Tailwind is used primarily for layout and spacing:
  - `flex`, `grid`, `gap-*`, `p-*`, `m-*`, `w-*`, `h-*`, `rounded-*`, `shadow-*`, `text-*` (sizes only), `font-*`
- Colors and surfaces come from tokens:
  - `bg-surface`, `text-fg`, `border-border`, `bg-elevated`, `text-muted`

## Theme Tokens (Semantic Palette)

Define semantic tokens with a minimal set (expand later if needed):

- `--bg` (app background)
- `--surface` (cards/panels)
- `--elevated` (modal/popover)
- `--fg` (primary text)
- `--muted` (secondary text)
- `--border`
- `--primary` (brand)
- `--primary-fg` (text on primary)
- `--danger`, `--warning`, `--success` (optional)
- `--ring` (focus outline)

### Light/Dark Definition

Implement as:

- `:root { ...light tokens... }`
- `.dark { ...dark tokens... }`

Toggling `.dark` on the root switches the entire app.

## Tailwind Integration Policy

### Tailwind config

Tailwind colors must reference CSS variables:

- `bg-surface` -> `background-color: rgb(var(--surface) / <alpha-value>)`
- `text-fg` -> `color: rgb(var(--fg) / <alpha-value>)`
- `border-border` -> `border-color: rgb(var(--border) / <alpha-value>)`

### Allowed Tailwind usage

- Layout: `flex`, `grid`, `gap`, `p`, `m`, `w`, `h`, `rounded`, `shadow`, `text-*` (sizes only), `font-*`
- Token-based color classes only: `bg-surface`, `text-fg`, `border-border`, `ring-ring`, etc.

### Disallowed Tailwind usage

- Literal color utilities: `text-red-500`, `bg-slate-900`, `bg-[#...]`, etc.
- Inline hex/rgb values and ad-hoc CSS variables.

## NiceGUI + Quasar Interop Rules

- Treat Quasar defaults as baseline for sizing/behavior.
- For colors, wrap UI with token-based container classes:
  - Page root container: `bg-bg text-fg`
  - Cards/panels: `bg-surface border-border`
- Avoid setting Quasar color props with raw names unless they map to tokens.

## Component Wrapper Convention

Every page uses a shared shell wrapper:

- `app/ui/components/layout/shell.py` applies `bg-bg text-fg min-h-screen`.
- All pages render inside Shell so background/text are consistent.

## Dark/Light Toggle Contract

### Single source of truth

- Keep `theme_mode` in a global store (e.g., `app/ui/state/app_store.py`).
- On toggle:
  - persist user preference
  - update root `.dark` class once
  - do not apply per-component changes

## Shared Style Assets

Add a dedicated theme folder and enforce usage:

```text
app/ui/styles/
  theme.css          # tokens: :root and .dark
  tailwind.css       # generated or minimal Tailwind entry
  components.css     # shared component classes (btn, card, input wrappers)
```

### components.css (shared classes)

Define canonical classes for repeating UI patterns:

- `.app-card` -> `bg-surface border border-border rounded-2xl p-4 shadow`
- `.app-section-title` -> `text-lg font-semibold text-fg`
- `.app-muted` -> `text-muted`
- `.app-btn-primary` -> `bg-primary text-primary-fg ...`

## Enforcement Checklist

- No raw colors in components (inline, hex, Tailwind literal palettes).
- Only semantic token classes for color/surface/border/ring.
- All pages render inside Shell wrapper.
- Dark/Light toggling only flips root `.dark`.
- Shared component classes used consistently.
- Any new token updates both light + dark definitions.
