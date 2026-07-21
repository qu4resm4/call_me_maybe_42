# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 15:50:25 by gquaresm            #+#    #+#            #
#   Updated: 2026/07/21 12:09:46 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
import importlib
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def print_execution_help() -> None:
    """
    Print execution instructions for setting up and running the project.

    Displays the recommended commands for running the application using
    either ``uv`` or a standard Python virtual environment with ``pip``.
    """
    project_root = Path(__file__).resolve().parent.parent
    print("=== HOW RUN THE PROJECT ===\n")
    print(f"  cd {project_root}\n")
    print("Recommended method (uv required):")
    print("  make install")
    print("  make run\n")
    print("  or\n")
    print("  uv sync")
    print("  uv run python -m src "
          "[--functions_definition <function_definition_file>] "
          "[--input <input_file>] "
          "[--output <output_file>]")
    print("\nAlternative method (venv and pip required):")
    print("  python -m venv .venv")
    print("  source .venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  pip install -e ./llm_sdk")
    print("  python -m src "
          "[--functions_definition <function_definition_file>] "
          "[--input <input_file>] "
          "[--output <output_file>]")
    print("\nDefault args values:"
          "\n--functions_definition data/input/functions_definition.json"
          "\n--input data/input/function_calling_tests.json"
          "\n--output data/output/function_calls.json\n")


def check_dependencies() -> None:
    """
    Verify that all required project dependencies are available.

    Attempts to import each required package before the application starts.
    If any dependency is missing, prints a dependency report, displays
    troubleshooting information when appropriate, shows execution
    instructions, and terminates the program with a non-zero exit code.
    """
    REQUIRED = [
        ("numpy", "Numerical computation"),
        ("pydantic", "Data validation"),
        ("json", "JSON serialization"),
        ("llm_sdk", "LLM inference wrapper"),
    ]
    check_available: dict[str, tuple[bool, str]] = {}
    pkg_msg: str = ""
    for pkg, description in REQUIRED:
        try:
            importlib.import_module(pkg)
            check_available[pkg] = (True, "")
            pkg_msg += (f"[OK] {pkg} - {description} installed\n")
        except (ImportError, PackageNotFoundError) as exc:
            pkg_msg += (f"[MISSING] {pkg} - {description} not installed\n")
            check_available[pkg] = (False, exc.msg)
    for pkg, available in check_available.items():
        if not available[0]:
            print(pkg_msg)
            if not check_available["llm_sdk"][0]:
                print(f"Details: {check_available["llm_sdk"][1]}")
                print(
                    "\nPossible causes:\n"
                    "- uv sync was not executed\n"
                    "- llm_sdk was not installed as a local dependency\n"
                    "- incorrect virtual environment\n"
                    "- execution outside the project environment\n"
                )
            print_execution_help()
            sys.exit(1)


def create_argument_parser() -> ArgumentParser:
    """
    Create and configure the application's command-line argument parser.

    Returns:
        ArgumentParser: A configured parser containing all supported
            command-line options and their default values.
    """
    parser = ArgumentParser(
        prog="call_me_maybe",
        description=(
            "Execute the function calling pipeline using the provided "
            "function definitions and input dataset."
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
        help="Path to the JSON file containing the function definitions.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/function_calling_tests.json"),
        metavar="FILE",
        help="Path to the input JSON file containing the test prompts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/function_calls.json"),
        metavar="FILE",
        help="Path where the generated function calls will be written.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen3-0.6B",
        metavar="MODEL",
        help="Model identifier used to execute the inference.",
    )
    return parser


def main() -> int:
    check_dependencies()
    args = create_argument_parser().parse_args()
    print(args.functions_definition)
    print(args.input)
    print(args.output)
    print(args.model)
    # Small_LLM_Model = import_or_exit()
    # model: Small_LLM_Model = Small_LLM_Model()
    # print(model)
    # print("vocab: ", model.get_path_to_vocab_file())
    # print("merges: ", model.get_path_to_merges_file())
    # print("tokenizer: ", model.get_path_to_tokenizer_file())

    # fazer loading dos arquivos
    return 0


if __name__ == "__main__":
    main()
    # raise SystemExit(main())
