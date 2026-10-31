# Contributing

1. Use Python 3.12+ and install the project with `python -m pip install -e ".[dev]"`.
2. Keep collectors independent of presentation and persist only the information needed for diagnostics.
3. Add or update tests for changes. Mock host metrics where possible so tests are portable.
4. Run `python -m pytest` and `ruff check .` before submitting.
5. Keep API exposure local unless authentication and deployment security are explicitly addressed.

Bug reports should include the operating system, Python version, command/API route, and a minimal reproduction. Do not include private logs or system details without reviewing them first.