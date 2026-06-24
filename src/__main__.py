#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 15:50:25 by gquaresm            #+#    #+#            #
#   Updated: 2026/06/23 21:32:41 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""
Ponto de entrada da aplicação.

Este arquivo tenta identificar problemas comuns de execução
e imprime instruções amigáveis para o usuário.
"""

from __future__ import annotations

import sys
from pathlib import Path


def print_execution_help() -> None:
    project_root = Path(__file__).resolve().parent.parent
    print("=== HOW RUN THE PROJECT ===\n")
    print("Recommended method (uv required):")
    print(f"  cd {project_root}")
    print("  uv sync")
    print("  make run")
    print("\nAlternative method (uv required):")
    print("  uv run python -m src")
    print("\nAlternative method (venv and pip required):")
    print("  python -m venv .venv")
    print("  source .venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  pip install -e ./llm_sdk")
    print("  python -m src")
    print()


def import_or_exit() -> type:
    """
    Tenta importar todas as dependências críticas.
    Em caso de erro, imprime instruções amigáveis.
    """
    err_msg = "ERROR: package '{pkg_name}' not found\n"
    # try:
    #     import numpy as np
    # except ModuleNotFoundError:
    #     print(err_msg.format(pkg_name="numpy"))
    #     print_execution_help()
    #     sys.exit(1)
    # try:
    #     import pydantic
    # except ModuleNotFoundError:
    #     print(err_msg.format(pkg_name="pydantic"))
    #     print_execution_help()
    #     sys.exit(1)
    try:
        from llm_sdk import Small_LLM_Model
        return Small_LLM_Model
    except ModuleNotFoundError as exc:
        print(err_msg.format(pkg_name="llm_sdk"))
        print(f"Details: {exc}")
        print(
            "\nPossible causes:\n"
            "- uv sync was not executed\n"
            "- llm_sdk was not installed as a local dependency\n"
            "- incorrect virtual environment\n"
            "- execution outside the project environment\n"
        )
        print_execution_help()
        sys.exit(1)


def main() -> int:
    Small_LLM_Model = import_or_exit()
    model = Small_LLM_Model()
    print(model)

    # fazer loading dos arquivos 
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
