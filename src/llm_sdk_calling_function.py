# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   llm_sdk_calling_function.py                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/20 22:35:54 by gquaresm            #+#    #+#            #
#   Updated: 2026/07/25 23:17:11 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
from pydantic import ConfigDict, validate_call
import os

from llm_sdk import Small_LLM_Model, torch    # type: ignore[attr-defined]

from src.schemas import FunctionDefinition


class Model_with_Calling_Function(Small_LLM_Model):

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
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
        # verificar se não está vazia 
        self.function_schemas.append(function_schemas)

    @validate_call
    def invoke_calling_function(
        self,
        prompt: str
    ) -> Any:
        """."""
        # verificar se não está vazio
        if len(self.function_schemas) == 0:
            msg = ("call_me_maybe: "
                   "It is necessary to associate function schemas.\n")
            raise Exception(msg)
        print("calling function: ", prompt)
        return ""

    #@validate_call
    #def invoke_calling_function(
    #    self,
    #    prompt: str
    #) -> Any:
    #     while not stop_condition:

    #     logits = backend.get_logits_from_input_ids(input_ids)

    #     logits = token_restrictor.restrict(
    #         logits,
    #         generation_state
    #     )

    #     next_token = token_selector.select(logits)

    #     input_ids.append(next_token)

    #     generation_state.update(next_token)

    #     if next_token == eos_token:
    #         break

    #     if generation_state.is_finished():
    #         break

    #     if len(generated) >= max_tokens:
    #         break

    @validate_call
    def invoke(
        self,
        prompt: str
    ) -> str:
        """."""
        # Tokeniza o prompt
        input_ids = self.encode(prompt)

        context: list[int] = input_ids.tolist()[0]

        print("primeiro contexto: ", context)
        print("tipo contexto: ", type(context))

        while True:
            # Obtém a distribuição para o próximo token
            logits = self.get_logits_from_input_ids(context)

            print(type(logits))
            print(logits[0])   # se for numpy/torch

            #os.system('cls' if os.name == 'nt' else 'clear')
            print("contexto: ", self.decode(context))
            # Escolhe um token (Greedy, por enquanto)
            # next_token = max(logits)   # argmax(logits)
            next_token_id: int = 0
            max_logit = logits[0]
            for token_id, logit in enumerate(logits):
                if max_logit < logit:
                    max_logit = logit
                    next_token_id = token_id

            # Acrescenta o token ao contexto
            context.append(next_token_id)

            # Verifica se terminou
            if next_token_id == self._tokenizer.eos_token_id:
                break

        return self.decode(context)

    def tradutor(self) -> str:
        context = [2753, 63834, 84, 1562, 281, 3413, 30, 362, 74506, 3958, 1643, 11, 9243, 297, 1709, 3958, 297, 281, 3413, 30, 506, 281, 3413, 3958, 4443, 452, 15027, 1709, 3958, 1152, 6357, 469,281, 3413, 11, 9243, 297, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30,506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506,63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30, 506, 63834, 84, 1562, 281, 3413, 30]
        return self.decode(context)
            


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



# classe para gerenciar estados da geração?
# generation_state.update? 
# teria que ter acesso ao model e etc que tem no small_llm

# ESTADOS SINTÁTICOS  ->  para garantir a sintaxe do json
# ESTADOS SEMANTICOS ->   para gerar o que tem a ver no 
# sentido e validar tipos  esperado = integer
#

