# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   llm_sdk_calling_function.py                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/20 22:35:54 by gquaresm            #+#    #+#            #
#   Updated: 2026/07/23 09:12:54 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
from pydantic import validate_call

from llm_sdk import Small_LLM_Model, torch    # type: ignore[attr-defined]

from src.schemas import FunctionDefinition


class Model_with_Calling_Function(Small_LLM_Model):

    @validate_call
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = True,
        token_selector: str = "greedy",  # or "sampling"
        token_restrictor: str = "dfa",  # or "trie" or "grammar"
    ) -> None:
        super().__init__(
                model_name,
                device=device,
                dtype=dtype,
                trust_remote_code=trust_remote_code
            )
        self.token_selector = token_selector
        self.token_restrictor = token_restrictor
        self.function_schemas: list = []

    @validate_call
    def bind_functions(
        self,
        function_schemas: list[FunctionDefinition]
    ) -> None:
        """."""
        # raise Exception("call_me_maybe: Invalid schema, "
        #                     "must be JSON-compatible\n", err)
        self.function_schemas.append(function_schemas)

    @validate_call
    def invoke_calling_function(
        self,
        prompt: str
    ) -> Any:
        """."""
        print("calling function: ", prompt)
        return ""


#         from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI

# # 1. Define the function using the @tool decorator
# @tool
# def multiply_numbers(a: int, b: int) -> int:
#     """Multiply two integers together. Use this tool whenever math
#  multiplication is required."""
#     return a * b

# # 2. Initialize your LLM model
# model = ChatOpenAI(model="gpt-4o", temperature=0)

# # 3. Bind the tool directly to the model
# model_with_tools = model.bind_tools([multiply_numbers])

# # 4. Invoke the model with a query requiring the tool
# user_query = "What is 42 multiplied by 7?"
# ai_message = model_with_tools.invoke(user_query)

# # 5. Inspect the generated tool call payload
# print("Tool Calls Request:")
# print(ai_message.tool_calls)

# # 6. Execute the actual function using the arguments provided by the model
# if ai_message.tool_calls:
#     tool_call = ai_message.tool_calls[0]
#     arguments = tool_call["args"] # Extract arguments dictionary

#     # Run the native function
#     result = multiply_numbers.invoke(arguments)
#     print(f"\nExecution Result: {result}")

    # método para registrar calling functions

    # método para invokar o modelo restritamente para calling functions

    # ? métodos privados para esse fluxo de saída estruturada

    # método de invokar o modelo com saída restrita (estruturada especifica 
    # json etc, receber por parametro qual a restrição)
    # para pode reutilizar para outras coisas, (chamada de pegar parametros, 
    # chamada de reconhecer função, invokar o modelo para obrigar uma saída
    # JSON estruturada especifica)

    #

    # pass

    # método para pegar os logits dos valores restritos de tipo
    #  (BOOLEAN, NUMBER (int e float), STRING, ETC)
    # para cada modelo > tokenizer.encode("true") > obtém os IDs > guarda
    #  internamente

    # ppara verificar se não for igual, verifica se o estado atual inclui

    # como saber quais tokens são validos: restrição em json qual algoritmo
    # ou qual mescla de algoritmos para que seja possível mais de um modelo
    # (por causa do tokenizador)

    # conversor de SCHEMA

    # parser que entende o schema e converte em validações iterativas
    # recebendo o modelo

    # método de gerar resposta comum (método) invoke
    # método

    # suporte a estrategias de

#     customizar a nível de ter o padrão Strategy e por opções como:

# ESCOLHA DE TOKEN:
# Greedy
# Sampling

# VERIFICAÇÃO DE TOKEN VALIDO:
# DFA
# Trie
# Grammar
