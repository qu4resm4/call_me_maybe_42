"""Focused tests for contracts and constrained-prefix validation."""

import json
import tempfile
import unittest
from pathlib import Path

from src.grammar import FunctionCallGrammar
from src.io_utils import InputFileError, load_model_list, write_json
from src.schemas import (
    FunctionCallingResult,
    FunctionDefinition,
    ParameterInfo,
    ParameterType,
    PromptInput,
)
from src.validator import ResultValidationError, validate_result


def definitions() -> list[FunctionDefinition]:
    """Return representative primitive function definitions."""
    return [
        FunctionDefinition(
            name="fn_add_numbers",
            description="Add numbers",
            parameters={
                "a": ParameterInfo(type=ParameterType.NUMBER),
                "b": ParameterInfo(type=ParameterType.NUMBER),
            },
            returns=ParameterInfo(type=ParameterType.NUMBER),
        ),
        FunctionDefinition(
            name="fn_greet",
            description="Greet someone",
            parameters={"name": ParameterInfo(type=ParameterType.STRING)},
            returns=ParameterInfo(type=ParameterType.STRING),
        ),
        FunctionDefinition(
            name="fn_is_even",
            description="Check parity",
            parameters={"n": ParameterInfo(type=ParameterType.INTEGER)},
            returns=ParameterInfo(type=ParameterType.BOOLEAN),
        ),
    ]


class ContractTests(unittest.TestCase):
    """Test file contracts and result validation."""

    def test_result_has_exact_shape(self) -> None:
        """Extra result fields must be rejected."""
        with self.assertRaises(ValueError):
            FunctionCallingResult.model_validate(
                {
                    "prompt": "x",
                    "name": "fn_greet",
                    "parameters": {"name": "Ada"},
                    "extra": "forbidden",
                }
            )

    def test_valid_and_invalid_result(self) -> None:
        """Declared primitive parameter types must be enforced."""
        valid = FunctionCallingResult(
            prompt="Greet Ada", name="fn_greet", parameters={"name": "Ada"}
        )
        self.assertIs(validate_result(valid, definitions()), valid)
        invalid = FunctionCallingResult(
            prompt="Is 2 even?", name="fn_is_even", parameters={"n": True}
        )
        with self.assertRaises(ResultValidationError):
            validate_result(invalid, definitions())

    def test_file_errors_are_actionable(self) -> None:
        """Missing and malformed files raise the domain error."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"
            with self.assertRaises(InputFileError):
                load_model_list(path, PromptInput)
            path.write_text("{", encoding="utf-8")
            with self.assertRaises(InputFileError):
                load_model_list(path, PromptInput)

    def test_output_parent_is_created(self) -> None:
        """Output serialization creates missing parent directories."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "result.json"
            write_json(path, [{"ok": True}])
            self.assertEqual(json.loads(path.read_text()), [{"ok": True}])


class GrammarTests(unittest.TestCase):
    """Test valid and invalid JSON prefixes."""

    def test_complete_calls(self) -> None:
        """The grammar accepts complete calls for each function."""
        grammar = FunctionCallGrammar(definitions())
        calls = (
            '{"name":"fn_add_numbers","parameters":{"a":2,"b":3}}',
            '{"name":"fn_greet","parameters":{"name":"Ada"}}',
            '{"name":"fn_is_even","parameters":{"n":4}}',
        )
        for call in calls:
            self.assertTrue(grammar.is_valid_prefix(call))
            self.assertTrue(grammar.is_complete(call))

    def test_invalid_calls_are_rejected(self) -> None:
        """Unknown functions, wrong types, and extra parameters are invalid."""
        grammar = FunctionCallGrammar(definitions())
        invalid = (
            '{"name":"unknown"',
            '{"name":"fn_greet","parameters":{"name":3}}',
            '{"name":"fn_greet","parameters":{"name":"Ada","x":1}}',
        )
        for call in invalid:
            self.assertFalse(grammar.is_valid_prefix(call))

    def test_escaped_string_prefix(self) -> None:
        """Escaped JSON string content remains a valid prefix."""
        grammar = FunctionCallGrammar(definitions())
        prefix = '{"name":"fn_greet","parameters":{"name":"A\\'
        self.assertTrue(grammar.is_valid_prefix(prefix))


if __name__ == "__main__":
    unittest.main()
