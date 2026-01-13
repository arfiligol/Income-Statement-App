# NiceGUI App Architecture (MVVM + Clean + DTO Discipline)

This document defines the non-negotiable architecture for the NiceGUI app.

## Goal

Build a maintainable NiceGUI application (web + optional native desktop via `ui.run(native=True)`) that:

- uses Material Icons + TailwindCSS for UI styling
- leverages Python for strong data analysis (pandas/numpy/etc.)
- supports system-native capabilities (e.g., file picker / file browser) and handles Excel files
- avoids callback spaghetti despite NiceGUI's event-driven UI lifecycle

## Core Principles (Non-Negotiable)

1. UI callbacks must never contain business workflows.
2. Cross-layer data exchange must use DTOs only.
3. Web vs native differences must be isolated in infrastructure gateways.

## Recommended High-Level Architecture

Combine:

- Clean-ish layers: `domain / application / infrastructure`
- MVVM for NiceGUI: `ui/pages/components + ui/viewmodels + ViewState/Intent/Effect`
- Optional `api/` only if external HTTP endpoints are needed.

## Layer Responsibilities

### domain/

- Pure rules and structures: DTOs, entities, validators, transformations, enums.
- No I/O, no pandas, no NiceGUI, no file system calls.

### application/

- Use cases for workflow orchestration (e.g., "Import Excel -> validate -> map -> compute -> export").
- Depends only on `domain` and `application/ports` (interfaces).
- No NiceGUI imports; avoid direct pandas/openpyxl (delegate to infra).

### infrastructure/

- External world: Excel I/O (pandas/openpyxl), file system, DB, web/native gateways.
- Implements interfaces defined in `application/ports`.
- Converts external formats into domain DTOs and returns DTOs.

### ui/

- Pages/components/layout + routing + ViewModels.
- Rendering, event wiring, state binding, and Effects.
- No heavy logic, no I/O, no pandas.

## MVVM Lifecycle Pattern for NiceGUI

### Key Constructs

- ViewState (single source of truth): one state object per page/feature.
- Intent/Command: all UI events become a finite set of intents.
- Effect channel: one-time side effects should not be stored in ViewState.

### Lifecycle Flow

1. View emits intent (or calls VM method).
2. ViewModel handles intent:
   - updates loading state
   - calls UseCase(s)
   - on success: updates state with DTO result
   - on failure: sets error state + emits Effect
3. View re-renders strictly from ViewState; side effects executed via Effects.

## Routing / Modularity in NiceGUI

- `ui/routers/*` for route registration.
- `ui/pages/*` for page composition.
- `ui/components/*` for reusable UI elements.

## Web + Native File Handling Strategy

Define a unified `FileSource` DTO:

- `LocalPathSource(path)` for native file dialog
- `UploadedTempSource(temp_path_or_id)` for web upload
- optional `BytesSource(bytes, filename)` if needed

UI always works with `FileSource`. Infrastructure resolves it into readable input.

## Background Task Strategy

Excel import and heavy compute must run off the UI thread.

- Provide a centralized `TaskRunner` (thread/process pool + async wrapper).
- ViewModel sets loading state immediately, awaits task completion, updates state/effects.

## Styling Strategy (Tailwind + Material Icons)

- Use Tailwind for layout (spacing/grid/typography/responsive).
- Keep component visuals aligned with NiceGUI/Quasar defaults; override minimally.
- Centralize icon names/mapping to avoid string scatter across the UI.
- Put minimal overrides in `app/ui/styles/` and apply a token-first theme (see style guide).

## Folder Structure (Recommended)

```text
your_app/
  main.py  # composition root: DI wiring, router registration, ui.run()

  app/
    config/
      settings.py
      logging.py

    common/
      errors.py
      types.py
      utils/

    domain/
      dto/
      entities/
      rules/
      enums.py

    application/
      use_cases/
      services/
      ports/
        repositories.py
        gateways.py

    infrastructure/
      repositories/
        excel_pandas_repo.py
      gateways/
        file_picker_web.py
        file_picker_native.py
        notifications.py
      runtime/
        task_runner.py
        paths.py

    ui/
      routers/
      pages/
      components/
        layout/
        widgets/
      viewmodels/
        base.py
      state/
        app_store.py
        session_store.py
      styles/
      static/

  tests/
    domain/
    application/
    infrastructure/
    ui_smoke/
```

## Review Checklist

- UI callbacks only emit intents / call VM methods (no workflow logic).
- No DataFrame/openpyxl/ORM objects leak above infrastructure.
- UseCases depend only on ports/interfaces, not infra implementations.
- Web/native differences exist only in infrastructure gateways.
- One ViewState per page is the single truth; no hidden UI state.
- Side effects go through Effects, not stored as persistent state.
