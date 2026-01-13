# Development Guide

## Environment Setup

This project uses `uv` for package management.

### Installation
```bash
    git clone https://github.com/arfiligol/Income-Statement-App.git
    cd Income-Statement-App
    uv sync
```

## Running the Application

### Standard Run
```bash
uv run start
```

### Hot Reload (Recommended for Dev)
NiceGUI supports hot reload via the `reload` flag. Enable it with:

```bash
NICEGUI_RELOAD=1 python main.py
```

## Packaging

Project packaging is handled by **Briefcase**.

1.  **Create**: `uv run briefcase create`
2.  **Build**: `uv run briefcase build`
3.  **Package**: `uv run briefcase package`

Artifacts are output to the `build/` directory.
