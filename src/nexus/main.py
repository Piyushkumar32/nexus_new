"""Python module entry point for the NEXUS CLI."""

from nexus.cli.commands import app


def main() -> None:
    app()