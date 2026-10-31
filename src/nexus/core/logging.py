"""Local application logging setup."""

import logging
from pathlib import Path


def configure_logging(level: str = "INFO", file_path: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if file_path:
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), handlers=handlers,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)