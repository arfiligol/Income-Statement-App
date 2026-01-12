# UI/UX Modernization: Web-Like Interface

## Overview
The application UI has been refactored to feel more like a modern web application, using a component-based architecture similar to React/Vue patterns.

## Architecture

```
src/views/
├── main_window.py              # Main window (assembles Navbar, Sidebar, ContentArea)
│
├── components/                 # Reusable UI primitives
│   ├── buttons.py              # PrimaryButton, SecondaryButton, IconButton, NavButton
│   ├── cards.py                # Card, InfoCard, FormCard
│   ├── inputs.py               # StyledLineEdit, FilePathInput
│   └── labels.py               # SectionTitle, StatusLabel, DescriptionLabel
│
├── layouts/                    # Structural layout components
│   ├── navbar.py               # Top navigation bar with hamburger menu
│   ├── sidebar.py              # Collapsible sidebar with navigation items
│   └── content_area.py         # Main content container (QStackedWidget wrapper)
│
├── pages/                      # Full-page views
│   ├── workflow/               # Workflow feature pages
│   │   ├── auto_fill_tab.py    # Tab 1: Auto Fill Lawyer Codes
│   │   ├── separate_ledger_tab.py  # Tab 2: Separate Ledger
│   │   └── workflow_page.py    # Assembled workflow page with tabs
│   └── database_page.py        # Database operations page
│
├── dialogs/                    # Modal dialogs
│   ├── lawyer_selection_dialog.py
│   └── update_dialog.py
│
├── styles/                     # Centralized styling (future)
│
└── _legacy/                    # Archived old views for reference
```

## Key Features

### Hamburger Menu & Collapsible Sidebar
- **Navbar** contains a hamburger button (☰) that toggles the sidebar visibility.
- **Sidebar** contains navigation items for switching between pages.
- Clicking the hamburger hides/shows the sidebar, similar to modern web apps.

### Tab-Based Workflow
- **WorkflowPage** uses `QTabWidget` to organize different workflows:
  - **Tab 1 (摘要抓律師代碼)**: Displays feature description and instructions.
  - **Tab 2 (律師收入明細)**: Contains output configuration (directory, filename).
- Tab switching automatically updates the controller's action state.

### Component Reusability
- All basic UI elements are defined in `components/` and imported by pages/layouts.
- Ensures visual consistency across the application.

## Design Principles
1. **Separation of Concerns**: Small, focused components.
2. **Consistent Styling**: Centralized in `components/` and `styles/`.
3. **MVC Compatibility**: View layer changes don't affect Controller/Model structure.
