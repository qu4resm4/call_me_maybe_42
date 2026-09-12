from __future__ import annotations

from dataclasses import dataclass, field
from math import inf
from typing import Optional

from generation_phase import GenerationPhase
from schemas import FunctionSchema, ParameterSchema, ParameterType


@dataclass
class GenerationState:
    functions: dict[str, FunctionSchema]

    phase: GenerationPhase = GenerationPhase.START

    selected_function: Optional[FunctionSchema] = None
    current_parameter: Optional[ParameterSchema] = None

    selected_parameters: set[str] = field(default_factory=set)

    function_buffer: str = ""
    parameter_buffer: str = ""
    value_buffer: str = ""

    json_output: str = ""

    def is_finished(self) -> bool:
        return self.phase == GenerationPhase.FINISHED

    def expected_type(self) -> Optional[ParameterType]:
        if self.current_parameter is None:
            return None

        return self.current_parameter.type

    def consume(self, text: str) -> None:
        self.json_output += text

        if self.phase == GenerationPhase.START:
            if text == "{":
                self.phase = GenerationPhase.FUNCTION_KEY
            return

        if self.phase == GenerationPhase.FUNCTION_KEY:
            self.function_buffer += text

            if self.function_buffer == '"function"':
                self.phase = GenerationPhase.ARGUMENTS_KEY

            return

        if self.phase == GenerationPhase.ARGUMENTS_KEY:
            if text == '"arguments"':
                self.phase = GenerationPhase.ARGUMENTS_VALUE
            return

        if self.phase == GenerationPhase.ARGUMENTS_VALUE:
            if text == "{":
                self.phase = GenerationPhase.PARAMETER_KEY
            return

        if self.phase == GenerationPhase.PARAMETER_KEY:
            self.parameter_buffer += text

            if text == '"':
                return

            if self.parameter_buffer.endswith('"'):
                name = self.parameter_buffer[1:-1]

                if self.selected_function is None:
                    return

                parameter = self.selected_function.parameters.get(name)

                if parameter is not None:
                    self.current_parameter = parameter
                    self.selected_parameters.add(name)
                    self.parameter_buffer = ""
                    self.phase = GenerationPhase.PARAMETER_VALUE

            return

        if self.phase == GenerationPhase.PARAMETER_VALUE:
            if self.current_parameter is None:
                return

            if self.current_parameter.type == ParameterType.STRING:
                self.value_buffer += text

            elif self.current_parameter.type in {
                ParameterType.INTEGER,
                ParameterType.NUMBER,
            }:
                self.value_buffer += text

            elif self.current_parameter.type == ParameterType.BOOLEAN:
                self.value_buffer += text

            return


class Constraint:
    def allowed(self, text: str, state: GenerationState) -> bool:
        raise NotImplementedError


class JsonConstraint(Constraint):
    def allowed(self, text: str, state: GenerationState) -> bool:
        if state.phase == GenerationPhase.START:
            return text.startswith("{")

        return True


class FunctionNameConstraint(Constraint):
    def __init__(self, functions: dict[str, FunctionSchema]):
        self.functions = functions

    def valid_prefix(self, value: str) -> bool:
        return any(
            name.startswith(value)
            for name in self.functions
        )

    def complete(self, value: str) -> bool:
        return value in self.functions


class StringConstraint(Constraint):
    def allowed(self, text: str, state: GenerationState) -> bool:
        return True


class BooleanConstraint(Constraint):
    VALUES = ("true", "false")

    def valid_prefix(self, value: str) -> bool:
        return any(
            candidate.startswith(value)
            for candidate in self.VALUES
        )


class NumberConstraint(Constraint):
    def allowed(self, value: str, integer: bool = False) -> bool:
        if not value:
            return True

        if value in {"-", "."}:
            return True

        if value.count("-") > 1:
            return False

        if "-" in value and not value.startswith("-"):
            return False

        if value.count(".") > 1:
            return False

        if integer and "." in value:
            return False

        return all(
            char.isdigit() or char in "-."
            for char in value
        )


class SchemaConstraint(Constraint):
    def __init__(self, state: GenerationState):
        self.state = state

    def allowed(self, text: str, state: GenerationState) -> bool:
        parameter_type = state.expected_type()

        if parameter_type is None:
            return True

        if parameter_type == ParameterType.STRING:
            return True

        if parameter_type == ParameterType.BOOLEAN:
            value = state.value_buffer + text
            return BooleanConstraint().valid_prefix(value)

        if parameter_type == ParameterType.INTEGER:
            value = state.value_buffer + text
            return NumberConstraint().allowed(
                value,
                integer=True,
            )

        if parameter_type == ParameterType.NUMBER:
            value = state.value_buffer + text
            return NumberConstraint().allowed(value)

        return True


class ConstraintEngine:
    def __init__(
        self,
        functions: dict[str, FunctionSchema],
    ):
        self.functions = functions

        self.function_constraint = FunctionNameConstraint(
            functions
        )

        self.json_constraint = JsonConstraint()

    def allowed(
        self,
        token_text: str,
        state: GenerationState,
    ) -> bool:

        if state.phase == GenerationPhase.START:
            return token_text == "{"

        if state.phase == GenerationPhase.FUNCTION_KEY:
            candidate = state.function_buffer + token_text

            if not '"function"'.startswith(candidate):
                return False

            return True

        if state.phase == GenerationPhase.ARGUMENTS_KEY:
            return token_text in {
                '"arguments"',
                ':',
                ',',
                '}',
            }

        if state.phase == GenerationPhase.ARGUMENTS_VALUE:
            return token_text == "{"

        if state.phase == GenerationPhase.PARAMETER_KEY:
            if state.selected_function is None:
                return False

            remaining = [
                name
                for name in state.selected_function.parameters
                if name not in state.selected_parameters
            ]

            candidate = state.parameter_buffer + token_text

            return any(
                f'"{name}"'.startswith(candidate)
                for name in remaining
            )

        if state.phase == GenerationPhase.PARAMETER_VALUE:
            return SchemaConstraint(state).allowed(
                token_text,
                state,
            )

        return False