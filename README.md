_This project has been created as part of the 42 curriculum by gquaresm._

# Call Me Maybe

## Description

Call Me Maybe is a function-calling pipeline for small causal language models. It receives natural-language prompts and a JSON file describing available functions, then produces one validated function call per prompt.

The model chooses the function and extracts its arguments. Constrained decoding controls the generated output token by token, so the final result is always a parseable JSON object with the required structure:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```

The default model is `Qwen/Qwen3-0.6B`. The model name can be changed through the existing command-line option for compatible models.

## Instructions

The project requires Python 3.10 or later and `uv`.

Install dependencies with:

```bash
uv sync
```

Run the default dataset with:

```bash
uv run python -m src
```

The command accepts the following options:

```text
--functions-definition FILE   Function definitions JSON file
--input FILE                 Prompt JSON file
--output FILE                Result JSON file
--model MODEL                Model identifier; Qwen/Qwen3-0.6B by default
```

For example:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

The output directory is created automatically. Invalid or missing input files produce a clear error and a non-zero exit status.

The Makefile provides `install`, `run`, `run-no-install`, `debug`, `clean`, `lint`, and `lint-strict` targets.

## Algorithm

The pipeline has five main stages:

1. Pydantic validates the function definitions and prompt input objects.
2. The model receives a model-formatted system and user prompt containing the available function definitions.
3. A runtime grammar compiles the function names, parameter names, JSON separators, and declared parameter types into accepted output prefixes.
4. For every generation step, the model returns logits. Invalid token continuations are excluded, and the greedy selector chooses the highest-scoring valid token.
5. The completed JSON object is parsed, normalized, validated against the selected function definition, and written to the output file.

The grammar restricts function names to the supplied definitions. It supports JSON strings, numbers, integers, booleans, arrays, and objects. String escaping and numeric lexical rules are checked before a token can be selected. The final Pydantic validation is an additional boundary check; it does not replace constrained decoding.

The selector and restrictor are independent. The current selector is deterministic greedy decoding. The grammar owns structural validity, while the selector owns the choice among valid logits.

## Design decisions

The application does not access private attributes of `llm_sdk`. The copied local SDK exposes public methods for chat-template rendering, vocabulary access, token text, special-token ids, and end-of-sequence metadata. This keeps tokenizer-specific behavior behind the SDK boundary.

Prompt formatting uses the selected model's chat template instead of hardcoding Qwen message delimiters. Qwen remains the mandatory default because it is the model required by the subject.

The public adapter was also validated with `microsoft/Phi-3-mini-4k-instruct`, which uses its own tokenizer chat template and vocabulary metadata. This confirms the model-agnostic path beyond Qwen. Compatibility still depends on the model exposing a causal-language-model interface and the tokenizer capabilities required by constrained decoding; multimodal checkpoints such as Ministral 3 are outside this SDK boundary.

The output uses the subject's `prompt`, `name`, and `parameters` keys. The bundled moulinette uses this exact contract. Numeric parameters declared as `number` are normalized to Python `float` values because the evaluator's reference functions require floats at runtime.

The decoder emits a compact JSON object without prose. This keeps the grammar finite and makes the result easy to validate while still allowing the model to choose among arbitrary function definitions supplied at runtime.

## Performance and reliability

The SDK caches model key/value attention states between consecutive logits requests. Without this cache, every token would require recomputing the entire prompt and generated sequence.

The greedy selector examines logits in descending order and stops at the first token accepted by the grammar. This is equivalent to selecting the maximum after masking invalid logits, while avoiding a full grammar parse for every low-scoring vocabulary item.

The public exercise set produced 11/11 valid and correct results in the local evaluation. The private exercise set produced 10/11, or 90.9%. The remaining private failure is a semantic extraction error in a template containing embedded quotation marks; the JSON structure and declared types remain valid.

## Testing strategy

Run the focused tests with:

```bash
python -m unittest discover -s tests -v
```

The tests cover Pydantic contracts, malformed and missing files, output-directory creation, valid and invalid grammar prefixes, escaped strings, and result validation.

Run static checks with:

```bash
uv run flake8 src llm_sdk tests
uv run mypy src --warn-return-any --warn-unused-ignores \
  --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

The bundled moulinette can be prepared in an isolated directory so it does not replace the repository's demonstration inputs:

```bash
cd moulinette
uv run python -m moulinette prepare_exercises \
  --set private --output /tmp/call_me_maybe_private_data
uv run python -m moulinette grade_student_answers \
  --set private \
  --student_answer_path /tmp/call_me_maybe_private_results.json
```

## Challenges

The main challenge is that a small model may produce a correct-looking answer followed by reasoning or prose. The decoder therefore stops only at an exact complete JSON object and rejects tokens that extend beyond the closing delimiter.

Another challenge is tokenizer variation. Token boundaries and chat delimiters differ between models, so the application uses public SDK capabilities rather than assuming Qwen's special tokens in its own code.

Natural-language extraction remains probabilistic. Constrained decoding guarantees structure and declared types, but semantic choices such as the exact regex text still depend on the model and prompt. The evaluation results are recorded above so this limitation is explicit.

## Resources and AI usage

The project subject and evaluation rubric are the primary requirements. Additional references include the Hugging Face documentation on chat templates and response parsing, and general references on autoregressive inference and constrained decoding.

AI assistance was used to inspect the repository, reason about the subject requirements, design the grammar and public SDK boundary, write implementation code, improve error handling, and create tests and documentation. All generated behavior was checked with local tests, static analysis, the Qwen model, and the bundled moulinette.
