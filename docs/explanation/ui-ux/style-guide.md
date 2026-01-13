
# UI Style Guide: Income Statement App

This document defines the visual design system for the **Income Statement App**, ensuring consistency across all views and components. All UI development must adhere to these guidelines.

## Technology Stack

- **Framework**: [NiceGUI](https://nicegui.io/) (based on Quasar/Vue)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) (Utility-first)
- **Icons**: Material Icons (via NiceGUI)

## Design Tokens

### Color Palette

We use a professional **"Slate & Indigo"** theme.

| Role | Color | Tailwind Class | Usage |
| :--- | :--- | :--- | :--- |
| **Primary** | Indigo 600 | `text-indigo-600` / `bg-indigo-600` | Main actions, active states, key highlights. |
| **Primary (Dark)** | Indigo 400 | `dark:text-indigo-400` | Primary color adapted for dark backgrounds. |
| **Success** | Emerald 600 | `text-emerald-600` / `bg-emerald-600` | Success messages, positive actions (e.g., "Run Separate Ledger"). |
| **Background (Light)** | Slate 50 | `bg-slate-50` | Main application background (light mode). |
| **Background (Dark)** | Slate 900 | `dark:bg-slate-900` | Main application background (dark mode). |
| **Surface (Light)** | White | `bg-white` | Cards, Sidebar, Panels. |
| **Surface (Dark)** | Slate 800 | `dark:bg-slate-800` | Cards, Sidebar, Panels in dark mode. |
| **Text (Body)** | Slate 700 | `text-slate-700` | Primary content text. |
| **Text (Muted)** | Slate 400 | `text-slate-400` | Secondary text, placeholders, descriptions. |
| **Border** | Slate 200 | `border-slate-200` | Dividers, card borders. |
| **Border (Dark)** | Slate 700 | `dark:border-slate-700` | Dividers, card borders in dark mode. |

### Typography

- **Font Family**: `Inter`, system-ui, sans-serif.
- **Headings**:
    - **H1 / Page Title**: `text-2xl font-bold tracking-tight text-slate-800 dark:text-white`
    - **H2 / Section Title**: `text-lg font-bold text-slate-800 dark:text-white`
- **Body**: `text-sm text-slate-600 dark:text-slate-300`
- **Labels**: `text-xs font-bold text-slate-400 dark:text-slate-500` (uppercase, tracking-wider)

### Iconography

- **Library**: **Google Material Icons (Filled)**.
- **Consistency**: Do not mix icon sets (e.g., FontAwesome, Ionicons). Always use the standard snake_case names from the Material set.
- **Standard Icons**:
    - **Toolbox**: `handyman` (not `tools` or `build`)
    - **Database**: `storage` (not `database`)
    - **Menu**: `menu`
    - **Dark Mode**: `dark_mode`
    - **Wallet**: `account_balance_wallet`

## Component Guidelines

### 1. Cards (Container)
Used to group related content.
- **Classes**: `w-full p-6 bg-white border border-slate-200 rounded-xl shadow-sm dark:bg-slate-800 dark:border-slate-700`
- **Note**: Use `p-4` or `p-6` depending on density required.

### 2. Buttons
- **Primary Action**: `bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm rounded-lg`
- **Secondary / Ghost**: `text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800`
- **Disabled State**: Reduce opacity (`opacity-50`) or use framework disable prop.

### 3. Inputs & Forms
- **Text Input**: `outlined dense` (Quasar props)
- **File Upload**: Custom styled using Tailwind to override Quasar defaults (see `workflow_view.py`).

### 4. Sidebar (Navigation)
- **Container**: `bg-white border-r border-slate-200 dark:!bg-slate-900 dark:!border-slate-800`
- **Items**: `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors`
- **Active State**: `text-indigo-600 bg-indigo-50` (or similar visual cue)

## Dark Mode Strategy

1.  **Tailwind Configuration**: `darkMode: 'class'` is enabled.
2.  **Implementation**:
    - Add `dark:` variant to **ALL** color-related utility classes.
    - Example: `bg-white dark:bg-slate-800 text-slate-900 dark:text-white`.
    - **Quasar Overrides**: Use `!important` (`!`) modifier or arbitrary selectors (e.g., `[&_.q-drawer]`) when Quasar components resist Tailwind styling.
3.  **Synchronization**: The `ui.dark_mode` toggle maps to `body.dark` class to ensure both Quasar and Tailwind work in sync.

## Layout Structure

```
+-------------------------------------------------------+
|  Header (Slate-900 / Dark: Slate-950)                 |
+--------------+----------------------------------------+
| Sidebar      | Page Content (Slate-50 / Slate-900)    |
| (Navigation) |                                        |
|              |  [ Page Title ]                        |
|              |                                        |
|              |  +----------------------------------+  |
|              |  | Step 1 Card                      |  |
|              |  | (White / Slate-800)              |  |
|              |  +----------------------------------+  |
|              |                                        |
+--------------+----------------------------------------+
```

### Layout Regions
1.  **Header**: Global application bar (Logo, Dark Mode Toggle).
2.  **Sidebar**: Main Navigation Menu.
3.  **Page Content**: The scrollable main area where Views (e.g., `WorkflowPage`, `DatabasePage`) are rendered.
    -   *Terminology*: We refer to the specific content loaded here as a **Page**.
