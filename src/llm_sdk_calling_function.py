"""Function-calling model wrapper with constrained JSON generation."""

import json
from typing import Any

from pydantic import ConfigDict, validate_call
import torch

from llm_sdk import Small_LLM_Model

from src.grammar import FunctionCallGrammar
from src.schemas import (
    FunctionCallingResult,
    FunctionDefinition,
    ChatMLRole,
    SystemMessage,
    UserMessage,
)
from src.strategies import GreedyTokenSelector
from src.validator import parse_and_validate_result


class GenerationError(RuntimeError):
    """Raised when constrained generation cannot complete a function call."""


class Model_with_Calling_Function(Small_LLM_Model):
    """Generate validated function calls with a local causal language model."""

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = True,
        token_selector: str = "greedy",
        max_tokens: int = 512,
        verbose: bool = True,
    ) -> None:
        super().__init__(
            model_name,
            device=device,
            dtype=dtype,
            trust_remote_code=trust_remote_code,
        )
        if token_selector != "greedy":
            raise ValueError("only the greedy token selector is supported")
        self._selector = GreedyTokenSelector()
        self._max_tokens = max_tokens
        self.verbose = verbose
        self.function_schemas: list[FunctionDefinition] = []
        self._vocabulary: dict[int, str] | None = None

    @validate_call
    def bind_functions(
        self,
        function_schemas: list[FunctionDefinition],
    ) -> None:
        """Replace the available function definitions for future calls."""
        if not function_schemas:
            raise ValueError("at least one function definition is required")
        names = [function.name for function in function_schemas]
        if len(names) != len(set(names)):
            raise ValueError("function names must be unique")
        self.function_schemas = list(function_schemas)
        if self.verbose:
            print(f"[call_me_maybe] bound {len(names)} function definitions")

    def format_prompt_to_calling_function(self, prompt: str) -> str:
        """Render a model-independent prompt with available definitions."""
        if not self.function_schemas:
            raise ValueError("bind_functions must be called before generation")
        definitions = [
            schema.model_dump(mode="json")
            for schema in self.function_schemas
        ]
        system = (
            "You are a function calling router. Choose the function that best "
            "matches the user's request. Return only one JSON object with "
            "exactly the keys name and parameters. Do not return markdown or "
            "explanations. Copy string arguments exactly from the user request"
            " without adding characters. Regex arguments must be raw regex "
            "patterns without slash delimiters or flags. "
            "The available functions are:\n"
            f"{json.dumps(definitions, ensure_ascii=False)}"
        )
        messages = [
            SystemMessage(role=ChatMLRole.SYSTEM, content=system).model_dump(),
            UserMessage(role=ChatMLRole.USER, content=prompt).model_dump(),
        ]
        return self.apply_chat_template(messages)

    def _get_vocabulary(self) -> dict[int, str]:
        """Load and cache decoded vocabulary token text."""
        if self._vocabulary is None:
            self._vocabulary = self.get_vocabulary()
        return self._vocabulary

    def invoke_calling_function(self, prompt: str) -> FunctionCallingResult:
        """Generate and validate one function call for ``prompt``."""
        if not self.function_schemas:
            raise GenerationError("no function definitions have been bound")
        grammar = FunctionCallGrammar(self.function_schemas)
        formatted_prompt = self.format_prompt_to_calling_function(prompt)
        if self.verbose:
            print(
                f"\n\n\n[call_me_maybe] context: {formatted_prompt}",
                end="",
                flush=True
            )
        input_ids = self.encode(formatted_prompt).tolist()[0]
        generated_ids: list[int] = []
        generated_text = ""
        vocabulary = self._get_vocabulary()
        special_token_ids = self.get_special_token_ids()

        for _ in range(self._max_tokens):
            if grammar.is_complete(generated_text):
                break
            logits = self.get_logits_from_input_ids(input_ids + generated_ids)
            try:
                token_id, checked = self._selector.select_valid(
                    logits,
                    vocabulary,
                    generated_text,
                    grammar.is_valid_prefix,
                    special_token_ids,
                )
            except ValueError as exc:
                raise GenerationError(
                    "no valid token remains after generated prefix: "
                    f"{generated_text!r}"
                ) from exc
            token_text = vocabulary[token_id]
            generated_ids.append(token_id)
            generated_text += token_text
            if self.verbose:
                print(
                    token_text,
                    end="",
                    flush=True
                )

        if not grammar.is_complete(generated_text):
            raise GenerationError(
                "maximum generation length reached before valid JSON"
            )
        try:
            raw_result: Any = json.loads(generated_text)
        except json.JSONDecodeError as exc:
            raise GenerationError(
                f"decoder produced invalid JSON: {exc}"
            ) from exc
        result = parse_and_validate_result(
            raw_result,
            prompt,
            self.function_schemas,
        )
        if self.verbose:
            print(f"\n\n[call_me_maybe] result: {result.model_dump_json()}")
        return result
