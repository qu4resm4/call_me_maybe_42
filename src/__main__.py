# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/16 15:50:25 by gquaresm            #+#    #+#            #
#   Updated: 2026/08/03 15:15:03 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import json
import sys
import importlib
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from src.llm_sdk_calling_function import Model_with_Calling_Function
from src.schemas import FunctionDefinition, PromptInput


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
    args = create_argument_parser().parse_args()   # primeira linha sempre
    check_dependencies()    # segunda linha antes da execução do PIPELINE
    print(args.functions_definition)
    print(args.input)
    print(args.output)
    print(args.model)

    function_schemas = []
    prompts_input = []

    try:
        with open(args.functions_definition) as f:
            function_schemas = [
                FunctionDefinition.model_validate(item)
                for item in json.load(f)
            ]
            # function_schemas = json.load(f)
        with open(args.input) as f:
            prompts_input = [
                PromptInput.model_validate(item)
                for item in json.load(f)
            ]
            # prompts_input = json.load(f)
    except Exception as err:
        print("call_me_maybe: error reading the files")
        if isinstance(err, TypeError):
            print("call_me_maybe: Invalid schema, "
                  "must be JSON-compatible\n", err)
            print("call_me_maybe: TypeError\n\n", err)
        sys.exit(1)

    llm = Model_with_Calling_Function(args.model)

    llm.bind_functions(function_schemas)

    json_responses = []
    for json_prompt in prompts_input:
        json_responses.append(llm.invoke_calling_function(json_prompt.prompt))
        # definir tipo de retorno () geração em json, conversão para esquema
        # entrega em esquema
        # conversão para json para escrita no arquivo após

    # Small_LLM_Model = import_or_exit()
    # model: Small_LLM_Model = Small_LLM_Model()
    # print(model)
    # print("vocab: ", model.get_path_to_vocab_file())
    # print("merges: ", model.get_path_to_merges_file())
    # print("tokenizer: ", model.get_path_to_tokenizer_file())

    # fazer loading dos arquivos
    return 0


def testes() -> None:
    args = create_argument_parser().parse_args()   # primeira linha sempre
    print(args.functions_definition)
    print(args.input)
    print(args.output)
    print(args.model)
    llm = Model_with_Calling_Function(args.model)
    # Supondo que 'instancia' seja o objeto que possui os seus métodos descritos

    # 1. Printar o Vocab File (Normalmente um JSON com mapeamento 'token': id)
    # try:
    #     path_vocab = llm.get_path_to_vocab_file()
    #     print(f"=== CONTEÚDO DO VOCABULÁRIO ({path_vocab}) ===")
    #     with open(path_vocab, 'r', encoding='utf-8') as f:
    #         vocab_data = json.load(f)
        
    #     # Como o vocabulário é gigante, printamos apenas os primeiros 20 itens para não travar o terminal
    #     primeiros_itens = dict(list(vocab_data.items())[:20])
    #     print(json.dumps(primeiros_itens, indent=4, ensure_ascii=False))
    #     print(f"... e mais {len(vocab_data) - 20} tokens.\n")
    # except Exception as e:
    #     print(f"Não foi possível ler o vocab_file: {e}\n")


    # # 2. Printar o Merges File (Arquivo de texto com os pares de junção do BPE)
    # try:
    #     path_merges = llm.get_path_to_merges_file()
    #     print(f"=== CONTEÚDO DO MERGES ({path_merges}) ===")
    #     with open(path_merges, 'r', encoding='utf-8') as f:
    #         # Lê as primeiras 20 linhas do arquivo de merges
    #         linhas_merges = [next(f).strip() for _ in range(20)]
        
    #     for linha in linhas_merges:
    #         print(linha)
    #     print("...\n")
    # except Exception as e:
    #     print(f"Não foi possível ler o merges_file: {e}\n")


    # # 3. Printar o Tokenizer File (O arquivo principal da biblioteca Hugging Face)
    # try:
    #     path_tokenizer = llm.get_path_to_tokenizer_file()
    #     print(f"=== CONTEÚDO DO TOKENIZER FILE ({path_tokenizer}) ===")
    #     with open(path_tokenizer, 'r', encoding='utf-8') as f:
    #         tokenizer_data = json.load(f)
    #         for line in f.readlines():
    #             print(line)
        
    #     # O tokenizer.json possui chaves estruturais importantes como "model" e "added_tokens"
    #     print("Chaves principais encontradas no arquivo:", list(tokenizer_data.keys()))
        
    #     # # Exibir especificamente a seção de added_tokens que você procura
    #     # if "added_tokens" in tokenizer_data:
    #     #     print("\n--- Seção 'added_tokens' dentro do tokenizer.json ---")
    #     #     print(json.dumps(tokenizer_data["added_tokens"][:15], indent=4, ensure_ascii=False))
    #     #     print(f"... total de {len(tokenizer_data['added_tokens'])} tokens adicionados.")
    #     # else:
    #     #     print("\nNenhuma chave 'added_tokens' explícita na raiz do JSON.")
    # except Exception as e:
    #     print(f"Não foi possível ler o tokenizer_file: {e}\n")


    # # Exemplo de uso para listar tokens adicionados e metadados
    # added_tokens_dict = llm._tokenizer.get_added_vocab()
    # sorted_added_tokens = dict(sorted(added_tokens_dict.items(), key=lambda item: item[1]))

    # print("--- LISTA DE ADDED TOKENS ---")
    # print(json.dumps(sorted_added_tokens, indent=4))

    # # Visualizar metadados brutos (special, lstrip, rstrip, etc.)
    # if llm._tokenizer.is_fast:
    #     tokenizer_json_meta = json.loads(llm._tokenizer._tokenizer.to_str())
    #     print("\n--- ESTRUTURA DO TOKENIZER.JSON ---")
    #     print(json.dumps(tokenizer_json_meta.get("added_tokens", [])[:5], indent=4))


    # print(llm._tokenizer.all_special_tokens)

    # print("chat template: ", llm._tokenizer.chat_template)
    # print("chat template: ", llm._tokenizer.apply_chat_template())
    # print("\nchat special tokens map: ", llm._tokenizer.special_tokens_map)


    #llm.invoke("Se meu nome é Gabriel Quaresma, qual seria meu nome primeiro nome?")

    #print(llm.format_prompt([
    #     {
    #         "role": "system",
    #         "content": "You are a friendly chatbot who always responds in the style of a pirate"
    #     },
    #     {
    #         "role": "user",
    #         "content": "How many helicopters can a human eat in one sitting?"
    #     }
    # ]))

    #def get_weather(location: str) -> str:
    #    """Gets the current weather for a location.
    
    #    Args:
    #        location: City and state, e.g. San Francisco, CA
    #    """
    #    return "22°C"

    #llm.bind_functions([
    #        {
    #            "name": "fn_greet",
    #            "description": "Generate a greeting message for a person by name.",
    #            "parameters": {
    #                "name": {"type": "string"}
    #            },
    #            "returns": {
    #                "type": "string"
    #            }
    #        }
    #    ])

    #formatted_text = llm.format_prompt_to_calling_function(
    #    messages=[
    #        {
    #            "role": "user",
    #            "content": "Me faça um elogio, meu nome é Gabriel Quaresma"
    #        }
    #    ]
    #)

#     llm.parse_response("""
# <|im_start|>user
# <|im_start|>system
# # Tools

# You may call one or more functions to assist with the user query.

# You are provided with function signatures within <tools></tools> XML tags:
# <tools>
# {"name": "fn_greet", "description": "Generate a greeting message for a person by name.", "parameters": {"name": {"type": "string"}}, "returns": {"type": "string"}}
# </tools>

# For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
# <tool_call>
# {"name": <function-name>, "arguments": <args-json-object>}
# </tool_call><|im_end|>
# <|im_start|>user
# Me faça um elogio, meu nome é Gabriel Quaresma<|im_end|>
# <|im_start|>assistant
# <|im_end|>
# <|im_start|>assistant
# <think>
# Okay, the user wants me to make a greeting. They mentioned their name is Gabriel Quaresma. Let me check the tools available. There's a function called fn_greet that takes a name parameter. I need to call that function with the name provided. I should format the tool call correctly in JSON inside the XML tags. Make sure the arguments are in JSON format and the name is a string. Alright, that should do it.
# </think>

# <tool_call>
# {"name": "fn_greet", "arguments": {"name": "Gabriel Quaresma"}}
# </tool_call><|im_end|>
# """)

    #print(formatted_text)

    #print(llm.invoke(formatted_text))
    # llm.invoke("Se meu nome é Gabriel Quaresma, qual seria meu nome primeiro nome?")
    
    # prompt formatado:
    """
    <|im_start|>system
    # Tools

    You may call one or more functions to assist with the user query.

    You are provided with function signatures within <tools></tools> XML tags:
    <tools>
    {"name": "fn_greet", "description": "Generate a greeting message for a person by name.", "parameters": {"name": {"type": "string"}}, "returns": {"type": "string"}}
    </tools>

    For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
    <tool_call>
    {"name": <function-name>, "arguments": <args-json-object>}
    </tool_call><|im_end|>
    <|im_start|>user
    Como está o tempo no Rio de Janeiro?<|im_end|>
    <|im_start|>assistant
    """

    # sobre a formatação, o decode é a nivel de leitura para palabras, 
    # então faz sentido limpar os tokens especiais. seria mais fácil splitar
    # a resposta da LLM enquanto os tokens exisitirem, só capturar o token id de cada marcação e usar para separar
    # 

    # enquanto gera captar o estado 
    # "nome da função e quando for selecionado um dos valores restritos
    #  daí aplica o schema escolhido para os argumentos, conforme o estado da geração no DFA


if __name__ == "__main__":
    testes()
    # main()
    # raise SystemExit(main())
