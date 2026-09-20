"""Validation of generated function calls against runtime definitions."""

from typing import Any

from pydantic import ValidationError

from src.schemas import (
    FunctionCallingResult,
    FunctionDefinition,
    ParameterType,
)


class ResultValidationError(ValueError):
    """Raised when a generated function call violates its definition."""


def _matches_type(value: Any, parameter_type: ParameterType) -> bool:
    """Return whether ``value`` has the exact JSON-compatible type required."""
    if parameter_type is ParameterType.INTEGER:
        return isinstance(value, int) and not isinstance(value, bool)
    if parameter_type is ParameterType.NUMBER:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if parameter_type is ParameterType.STRING:
        return isinstance(value, str)
    if parameter_type is ParameterType.BOOLEAN:
        return isinstance(value, bool)
    if parameter_type is ParameterType.ARRAY:
        return isinstance(value, list)
    if parameter_type is ParameterType.OBJECT:
        return isinstance(value, dict)
    return False


def validate_result(
    result: FunctionCallingResult,
    definitions: list[FunctionDefinition],
) -> FunctionCallingResult:
    """Validate a result against the selected function definition."""
    definitions_by_name = {
        definition.name: definition
        for definition in definitions
    }
    definition = definitions_by_name.get(result.name)
    if definition is None:
        raise ResultValidationError(f"unknown function: {result.name}")

    expected_names = set(definition.parameters)
    actual_names = set(result.parameters)
    missing = expected_names - actual_names
    extra = actual_names - expected_names
    if missing:
        raise ResultValidationError(
            f"function {result.name} is missing parameters: {sorted(missing)}"
        )
    if extra:
        raise ResultValidationError(
            f"function {result.name} has extra parameters: {sorted(extra)}"
        )

    for name, parameter in definition.parameters.items():
        if not _matches_type(result.parameters[name], parameter.type):
            actual_type = type(result.parameters[name]).__name__
            raise ResultValidationError(
                f"parameter {name} must be {parameter.type.value}, "
                f"got {actual_type}"
            )
    return result


def parse_and_validate_result(
    raw: Any,
    prompt: str,
    definitions: list[FunctionDefinition],
) -> FunctionCallingResult:
    """Build and validate a result from model-produced JSON data."""
    if isinstance(raw, dict):
        raw = dict(raw)
        selected_name = raw.get("name")
        definition = next(
            (
                item
                for item in definitions
                if item.name == selected_name
            ),
            None,
        )
        if definition is not None:
            parameters = dict(raw.get("parameters", {}))
            for name, parameter in definition.parameters.items():
                value = parameters.get(name)
                if (
                    parameter.type is ParameterType.NUMBER
                    and isinstance(value, int)
                    and not isinstance(value, bool)
                ):
                    parameters[name] = float(value)
            raw["parameters"] = parameters
    try:
        result = FunctionCallingResult.model_validate(
            {"prompt": prompt, **raw} if isinstance(raw, dict) else raw
        )
    except ValidationError as exc:
        raise ResultValidationError(
            f"invalid function-call object: {exc}"
        ) from exc
    return validate_result(result, definitions)
