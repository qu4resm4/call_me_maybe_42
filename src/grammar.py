"""A finite JSON grammar for the function-calling output contract."""

import json
import re
from dataclasses import dataclass

from src.schemas import FunctionDefinition, ParameterType


_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]*)?(?:[eE][+-]?[0-9]*)?")
_COMPLETE_NUMBER = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
)


@dataclass(frozen=True)
class PrefixResult:
    """Result of parsing a generated prefix."""

    valid: bool
    complete: bool = False
    position: int = 0


def _partial_literal(text: str, position: int, literal: str) -> PrefixResult:
    """Validate a literal that may be only partially present."""
    remaining = text[position:]
    if literal.startswith(remaining):
        return PrefixResult(True, len(remaining) == len(literal), len(text))
    if remaining.startswith(literal):
        return PrefixResult(True, True, position + len(literal))
    return PrefixResult(False)


def _scan_string(text: str, position: int) -> PrefixResult:
    """Scan one JSON string, allowing an unfinished final string."""
    if position >= len(text) or text[position] != '"':
        return PrefixResult(False)
    index = position + 1
    escaped = False
    while index < len(text):
        char = text[index]
        if escaped:
            if char not in '"\\/bfnrtu':
                return PrefixResult(False)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return PrefixResult(True, True, index + 1)
        elif ord(char) < 0x20:
            return PrefixResult(False)
        index += 1
    return PrefixResult(True, False, len(text))


def _scan_json_value(text: str, position: int) -> PrefixResult:
    """Scan an array/object value until its top-level close delimiter."""
    if position >= len(text) or text[position] not in "[{":
        return PrefixResult(False)
    stack: list[str] = [text[position]]
    index = position + 1
    escaped = False
    in_string = False
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                if char not in '"\\/bfnrtu':
                    return PrefixResult(False)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            elif ord(char) < 0x20:
                return PrefixResult(False)
        else:
            if char == '"':
                in_string = True
            elif char in "[{":
                stack.append(char)
            elif char in "]}":
                if not stack or (char == "]" and stack[-1] != "[") or (
                    char == "}" and stack[-1] != "{"
                ):
                    return PrefixResult(False)
                stack.pop()
                if not stack:
                    return PrefixResult(True, True, index + 1)
        index += 1
    return PrefixResult(True, False, len(text))


def _value_prefix(
    text: str,
    position: int,
    parameter_type: ParameterType,
) -> PrefixResult:
    """Validate a primitive or container value prefix."""
    if parameter_type is ParameterType.STRING:
        return _scan_string(text, position)
    if parameter_type in (ParameterType.ARRAY, ParameterType.OBJECT):
        result = _scan_json_value(text, position)
        if result.complete:
            try:
                value = json.loads(text[position:result.position])
            except json.JSONDecodeError:
                return PrefixResult(False)
            expected = list if parameter_type is ParameterType.ARRAY else dict
            if not isinstance(value, expected):
                return PrefixResult(False)
        return result

    end = position
    while end < len(text) and text[end] not in ",}":
        end += 1
    raw = text[position:end]
    if parameter_type is ParameterType.BOOLEAN:
        valid_values = ("true", "false")
        valid = any(
            value.startswith(raw)
            for value in valid_values
        )
        complete = raw in valid_values
    elif parameter_type is ParameterType.INTEGER:
        valid = bool(_NUMBER.fullmatch(raw) or re.fullmatch(r"-?", raw))
        complete = bool(
            re.fullmatch(r"-?(?:0|[1-9][0-9]*)", raw)
        )
    else:
        valid = bool(
            _NUMBER.fullmatch(raw) or re.fullmatch(r"-?", raw)
        )
        complete = bool(_COMPLETE_NUMBER.fullmatch(raw))
    if not valid or (end < len(text) and not complete):
        return PrefixResult(False)
    return PrefixResult(True, end < len(text) and complete, end)


class FunctionCallGrammar:
    """Validate prefixes of the exact function-call JSON object."""

    def __init__(self, definitions: list[FunctionDefinition]) -> None:
        self.definitions = definitions
        self._names = {definition.name for definition in definitions}
        self._cache: dict[str, bool] = {}

    def is_valid_prefix(self, prefix: str) -> bool:
        """Return whether ``prefix`` can be extended to a valid call."""
        if prefix in self._cache:
            return self._cache[prefix]
        value = self._parse(prefix).valid
        self._cache[prefix] = value
        return value

    def is_complete(self, text: str) -> bool:
        """Return whether ``text`` is a complete valid call object."""
        parsed = self._parse(text)
        return (
            parsed.valid
            and parsed.complete
            and parsed.position == len(text)
        )

    def _parse(self, text: str) -> PrefixResult:
        base = '{"name":'
        if not text.startswith(base):
            return PrefixResult(base.startswith(text), False, len(text))

        name_result = _scan_string(text, len(base))
        if not name_result.valid or not name_result.complete:
            fragment = text[len(base):]
            valid = any(
                json.dumps(name).startswith(fragment)
                for name in self._names
            )
            return PrefixResult(valid, False, len(text))
        try:
            selected_name = json.loads(text[len(base):name_result.position])
        except json.JSONDecodeError:
            return PrefixResult(False)
        if selected_name not in self._names:
            return PrefixResult(False)

        after_name = ',"parameters":{'
        literal_result = _partial_literal(
            text,
            name_result.position,
            after_name,
        )
        if not literal_result.valid or not literal_result.complete:
            return literal_result
        position = name_result.position + len(after_name)
        definition = next(
            item for item in self.definitions if item.name == selected_name
        )

        for index, (parameter_name, parameter_info) in enumerate(
            definition.parameters.items()
        ):
            key = json.dumps(parameter_name) + ":"
            key_result = _partial_literal(text, position, key)
            if not key_result.valid or not key_result.complete:
                return key_result
            position += len(key)

            value_result = _value_prefix(text, position, parameter_info.type)
            if not value_result.valid or not value_result.complete:
                return value_result
            position = value_result.position

            separator = "," if index < len(definition.parameters) - 1 else "}}"
            separator_result = _partial_literal(text, position, separator)
            if not separator_result.valid or not separator_result.complete:
                return separator_result
            if index == len(definition.parameters) - 1 and (
                position + len(separator) != len(text)
            ):
                return PrefixResult(False)
            position += len(separator)

        if not definition.parameters:
            end_result = _partial_literal(text, position, "}}")
            return PrefixResult(
                end_result.valid,
                end_result.complete,
                len(text),
            )
        return PrefixResult(True, position == len(text), position)

    def allowed_token_ids(
        self,
        prefix: str,
        vocabulary: dict[int, str],
        special_token_ids: set[int],
    ) -> set[int]:
        """Return vocabulary ids whose text keeps the grammar valid."""
        return {
            token_id
            for token_id, token_text in vocabulary.items()
            if token_id not in special_token_ids
            and token_text
            and self.is_valid_prefix(prefix + token_text)
        }
