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
We provide a hot-reload script that watches for changes in the `app/` directory and restarts the application automatically.

```bash
uv run python devtools/auto_reload.py
```

## Packaging

Project packaging is handled by **Briefcase**.

1.  **Create**: `uv run briefcase create`
2.  **Build**: `uv run briefcase build`
3.  **Package**: `uv run briefcase package`

Artifacts are output to the `build/` directory.
