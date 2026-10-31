# Development Guide

## Environment Setup

1. Python 3.12+ is required.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install editable package with development dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Code Quality Standards

We use `ruff` for linting and code formatting:
```bash
ruff check src tests
ruff format src tests
```
