"""Input validation and result serialization helpers."""

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


class InputFileError(Exception):
    """Raised when a configured JSON input cannot be loaded or validated."""


def load_model_list(path: Path, model_type: type[ModelT]) -> list[ModelT]:
    """Load and validate a JSON array of Pydantic models from ``path``."""
    try:
        with path.open(encoding="utf-8") as file:
            raw: Any = json.load(file)
    except FileNotFoundError as exc:
        raise InputFileError(f"file not found: {path}") from exc
    except OSError as exc:
        raise InputFileError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputFileError(
            f"invalid JSON in {path} at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(raw, list):
        raise InputFileError(f"{path} must contain a JSON array")

    try:
        return [model_type.model_validate(item) for item in raw]
    except ValidationError as exc:
        raise InputFileError(f"invalid data in {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    """Write JSON to ``path``, creating its parent directory if necessary."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(value, file, indent=2, ensure_ascii=False)
            file.write("\n")
    except OSError as exc:
        raise InputFileError(f"cannot write {path}: {exc}") from exc
