# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   llm_sdk_calling_function.py                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/20 22:35:54 by gquaresm            #+#    #+#            #
#   Updated: 2026/07/31 10:55:09 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any, cast

from pydantic import ConfigDict, validate_call

from llm_sdk import Small_LLM_Model, torch    # type: ignore[attr-defined]

from src.schemas import ChatMLRole, ChatMLTemplate, FunctionDefinition


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
        self.function_schemas: list[dict] = []
        self._max_tokens: int = 20000    # vinte mil

    @validate_call
    def bind_functions(
        self,
        function_schemas: list[FunctionDefinition]
    ) -> None:
        """."""
        self.function_schemas.append(*[
            func.model_dump(exclude_none=True) for func in function_schemas
        ])

    @validate_call
    def format_prompt(self, messages: list[ChatMLTemplate]) -> str:
        """."""
        formatted_messages = [
            msg.model_dump(exclude_none=True) for msg in messages
        ]
        return_value = self._tokenizer.apply_chat_template(
            formatted_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        if isinstance(return_value, str):
            return return_value
        return ""

    @validate_call
    def format_prompt_to_calling_function(
        self,
        messages: list[ChatMLTemplate]
    ) -> str:
        """."""
        if len(self.function_schemas) == 0:
            msg = ("call_me_maybe: "
                   "It is necessary to associate function schemas.\n")
            raise Exception(msg)
        # Converter os modelos Pydantic de volta para dicts para o transformers
        formatted_messages = [
            msg.model_dump(exclude_none=True) for msg in messages
        ]
        return_value = self._tokenizer.apply_chat_template(
            formatted_messages,
            tools=[*self.function_schemas],
            tokenize=False,
            add_generation_prompt=True
        )
        return return_value

    @validate_call
    def parse_response(
        self,
        response: str
    ) -> list[dict[str, str]]:
        """ reverso do apply_chat_template que usa os otkens especificos
         do modelo que delimita cada coisa"""
        schema = ChatMLTemplate.model_json_schema()
        r_value = self._tokenizer.parse_response(response, schema)
        #r_value = self._tokenizer.parse_response(response)
        # Normalize returned value to list[dict[str, str]] for Pylance e Mypy
        print("r_value fdp:", r_value)
        return r_value


# import re
# from transformers import AutoTokenizer

# def parse_response_dynamically(response_text: str, tokenizer: AutoTokenizer) -> list[dict]:
#     """
#     Tenta decodificar o texto de qualquer LLM lendo seus atributos de chat e tokens nativos.
#     """
#     # 1. Tenta usar o recurso nativo de parsing do transformers (se o modelo já suportar)
#     if getattr(tokenizer, "response_schema", None) is not None:
#         try:
#             return tokenizer.parse_response(response_text)
#         except Exception:
#             pass

#     # 2. Descobre tokens especiais diretamente do tokenizer do modelo
#     special_tokens = list(tokenizer.all_special_tokens)
    
#     # 3. Detecta os marcadores de role inspecionando o Jinja Chat Template
#     chat_template = getattr(tokenizer, "chat_template", "") or ""
    
#     # Padrão ChatML (<|im_start|>, <|im_end|>)
#     if "<|im_start|>" in chat_template or "<|im_start|>" in special_tokens:
#         pattern = r"<\|im_start\|>(\w+)\n?(.*?)(?=<\|im_end\|>|$)"
#         matches = re.findall(pattern, response_text, re.DOTALL)
#         if matches:
#             return [{"role": role.strip(), "content": content.strip()} for role, content in matches]

#     # Padrão Llama 3 / Qwen 2.5 (<|start_header_id|> user <|end_header_id|>)
#     if "<|start_header_id|>" in chat_template or "<|start_header_id|>" in special_tokens:
#         pattern = r"<\|start_header_id\|>(\w+)<\|end_header_id\|>\n\n(.*?)(?=<\|eot_id\|>|<|start_header_id\|>|$)"
#         matches = re.findall(pattern, response_text, re.DOTALL)
#         if matches:
#             return [{"role": role.strip(), "content": content.strip()} for role, content in matches]

#     # Padrão Mistral / Llama 2 ([INST] ... [/INST])
#     if "[INST]" in chat_template or "[INST]" in special_tokens:
#         # Mistral não marca claramente a resposta do assistente com tags específicas,
#         # ela fica apenas fora do [INST]
#         clean_text = re.sub(r"\[INST\].*?\[/INST\]", "", response_text, flags=re.DOTALL).strip()
#         # Remove EOS tokens do modelo
#         for eos in [tokenizer.eos_token, "</s>"]:
#             if eos:
#                 clean_text = clean_text.replace(eos, "").strip()
#         return [{"role": "assistant", "content": clean_text}]

#     # Fallback genérico: Limpa tokens de fim de texto (EOS/PAD) e assume que é a resposta do assistente
#     clean_text = response_text
#     for token in tokenizer.all_special_tokens:
#         clean_text = clean_text.replace(token, "")
    
#     return [{"role": "assistant", "content": clean_text.strip()}]


    # @validate_call
    # def invoke_calling_function(
    #    self,
    #    prompt: str
    # ) -> Any:
    #     """;"""
    #     if len(self.function_schemas) == 0:
    #         msg = ("call_me_maybe: "
    #                "It is necessary to associate function schemas.\n")
    #         raise Exception(msg)

    #     input_ids = self.encode(prompt)
        
    #     context: list[int] = input_ids.tolist()[0]
        
    #     print("primeiro contexto: ", context)
    #     print("tipo contexto: ", type(context))

    #     stop_condition = False
    #     while not stop_condition:
    #         logits = self.get_logits_from_input_ids(input_ids)
    #         logits = token_restrictor.restrict(
    #             logits,
    #             generation_state
    #         )
    #         next_token = token_selector.select(logits)
    #         input_ids.append(next_token)
    #         generation_state.update(next_token)
    #         if next_token == eos_token:
    #             break
    #         if generation_state.is_finished():
    #             break
    #         if len(generated) >= self._max_tokens:
    #             break
            
    #     token_str = self.decode(context)
    #     response = self.parse_response(token_str)
    #     # pegar a última mensagem de assistant?
    #     return response

    @validate_call
    def invoke(
        self,
        prompt: str | list[ChatMLTemplate]
    ) -> str:
        """."""
        # Tokeniza o prompt
        import os

        if isinstance(prompt, str):
            prompt = [
                ChatMLTemplate(
                    role=ChatMLRole.USER.value,
                    content=prompt
                )
            ]
        formatted_prompt = self.format_prompt(prompt)

        input_ids = self.encode(formatted_prompt)

        context: list[int] = input_ids.tolist()[0]

        while True:
            # Obtém a distribuição para o próximo token
            logits = self.get_logits_from_input_ids(context)

            os.system('cls' if os.name == 'nt' else 'clear')
            print("contexto atual: ", self.decode(context))

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

        # token_str = self.decode(context)
        token_str = self._tokenizer.decode(context, skip_special_tokens=False)
        print("TESTES sem skip", token_str)
        response = self.parse_response(token_str)
        # pegar a última mensagem de assistant?
        print("printando response", response)
        return response

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

