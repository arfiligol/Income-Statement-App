# NiceGUI Guardrails (Official Docs Alignment)

This document defines the minimum compliance rules for NiceGUI usage in this app.

## Official References

- Page Layout: https://nicegui.io/documentation/section_page_layout
- Controls: https://nicegui.io/documentation/section_controls
- Binding Properties: https://nicegui.io/documentation/section_binding_properties
- Styling & Appearance: https://nicegui.io/documentation/section_styling_appearance
- Action & Events: https://nicegui.io/documentation/section_action_events
- Pages & Routing: https://nicegui.io/documentation/section_pages_routing

## Guardrails

### Page Layout

- Use `with` context for UI tree composition; do not pass parent explicitly.
- Prefer `ui.row`, `ui.column`, `ui.card`, `ui.grid`, and layout elements (header/drawer/footer) for structure.
- Do not mix unrelated layouts in a single function; isolate into components.

### Controls

- Use NiceGUI controls (`ui.button`, `ui.input`, `ui.select`, `ui.upload`, etc.) with explicit handlers.
- Event handlers only dispatch intents or call ViewModel methods (no workflows in UI).
- Use `ui.upload` for web uploads and native dialogs for desktop via gateways.

### Binding Properties

- Use `bind_value`, `bind_text_from`, or `bind_visibility` only for simple, local UI sync.
- Avoid heavy binding over large or complex objects (active link refresh loop can be expensive).
- When binding to custom models, prefer bindable properties or bindable dataclasses if needed.

### Styling & Appearance

- Use `classes` and `props` for styling; avoid inline `style` unless unavoidable.
- Apply Tailwind classes for layout; colors must come from semantic tokens.
- Dark mode uses a single root switch (`ui.dark_mode` + root `.dark` class).
- When overriding Quasar, use Tailwind layers or `ui.add_css` as documented.

### Action & Events

- Use async handlers or background tasks for I/O-bound and CPU-bound work.
- Avoid blocking event handlers; prefer task runner or async workflows.
- Use `ui.notify`, `ui.dialog`, and `ui.run_javascript` as documented for effects only.

### Pages & Routing

- Use `@ui.page` on free functions or static methods only.
- Use `ui.navigate.to` for navigation (`ui.open` is removed).
- Route registration happens at startup (composition root).

## App-Specific Enforcement

- UI callbacks emit intents and call ViewModels only.
- DTOs are the only cross-layer data structures.
- Web/native differences are isolated in infrastructure gateways.
- One ViewState per page; effects are not stored in state.
