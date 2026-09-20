"""Command-line entry point for the function-calling pipeline."""

import importlib
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from importlib.metadata import PackageNotFoundError
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.io_utils import (  # noqa: E402
    InputFileError,
    load_model_list,
    write_json,
)
from src.llm_sdk_calling_function import (  # noqa: E402
    GenerationError,
    Model_with_Calling_Function,
)  # noqa: E402
from src.schemas import FunctionDefinition, PromptInput  # noqa: E402


def create_argument_parser() -> ArgumentParser:
    """Create the command-line argument parser."""
    parser = ArgumentParser(
        prog="call_me_maybe",
        description=(
            "Generate validated function calls from natural-language prompts."
        ),
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--functions-definition",
        "--functions_definition",
        dest="functions_definition",
        type=Path,
        default=Path("data/input/functions_definition.json"),
        metavar="FILE",
        help="JSON file containing function definitions.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/function_calling_tests.json"),
        metavar="FILE",
        help="JSON file containing prompt objects.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/function_calling_results.json"),
        metavar="FILE",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-0.6B",
        metavar="MODEL",
        help="Model identifier used for inference.",
    )
    return parser


def check_dependencies() -> None:
    """Raise a clear error when a required package is not installed."""
    required = ("numpy", "pydantic", "llm_sdk")
    missing: list[str] = []
    for package in required:
        try:
            importlib.import_module(package)
        except (ImportError, PackageNotFoundError):
            missing.append(package)
    if missing:
        raise InputFileError(
            "missing dependencies: " + ", ".join(missing) + ". Run `uv sync`."
        )


def main() -> int:
    """Run the complete input, generation, validation, and output pipeline."""
    args = create_argument_parser().parse_args()
    try:
        check_dependencies()
        definitions = load_model_list(
            args.functions_definition,
            FunctionDefinition,
        )
        prompts = load_model_list(args.input, PromptInput)
        trust_remote_code = args.model != "microsoft/Phi-3-mini-4k-instruct"
        model = Model_with_Calling_Function(
            args.model,
            verbose=True,
            trust_remote_code=trust_remote_code,
        )
        model.bind_functions(definitions)
        results = [
            model.invoke_calling_function(item.prompt) for item in prompts
        ]
        write_json(
            args.output,
            [result.model_dump(mode="json") for result in results],
        )
    except (InputFileError, GenerationError, ValueError, OSError) as exc:
        print(f"call_me_maybe: error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - final CLI safety boundary
        print(f"call_me_maybe: unexpected error: {exc}", file=sys.stderr)
        return 1
    print(f"call_me_maybe: wrote {len(results)} results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
