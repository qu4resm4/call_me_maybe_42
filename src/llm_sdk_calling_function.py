# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   llm_sdk_calling_function.py                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/20 22:35:54 by gquaresm            #+#    #+#            #
#   Updated: 2026/08/16 12:41:58 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import cast, Any

import re
import json

from pydantic import ConfigDict, validate_call

from llm_sdk import Small_LLM_Model, torch    # type: ignore[attr-defined]

from src.schemas import (
    AssistantMessage,
    ChatMLRole,
    FunctionDefinition,
    SystemMessage,
    ToolCall,
    ToolMessage,
    UserMessage,
    ChatMessage
)
from src.constraints import GenerationState
from src.token_restrictors import DFAConstrainedRestrictor
from src.implementations import GreedySelector


class Model_with_Calling_Function(Small_LLM_Model):

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-0.6B",
        *,
        device: str | None = None,
        dtype: torch.dtype | None = None,
        trust_remote_code: bool = True,
        verbose_mode: bool = False,
        # token_selector: str = "greedy",  # or "sampling" #não faz sentido vou acabar tirando isso
        # token_restrictor: str = "dfa",  # or "trie" or "grammar" #não faz sentido vou acabar tirando isso
        max_tokens: int = 20000    # vinte mil
    ) -> None:
        super().__init__(
                model_name,
                device=device,
                dtype=dtype,
                trust_remote_code=trust_remote_code
            )
        # self.token_selector = token_selector
        # self.token_restrictor = token_restrictor
        self.function_schemas: list[dict] = []
        self._max_tokens: int = max_tokens
        self.verbose_mode: bool = verbose_mode

        start, end = self.__discover_message_delimiters()
        self.message_start_str: str = start
        self.message_end_str: str = end
        self.message_start_token: int = self.encode(start).tolist()[0][0]
        self.message_end_token: int = self.encode(end).tolist()[0][0]
        if self.verbose_mode:
            print(f"start: {start}, end: {end}")
            print("message_start_token: ", self.message_start_token)
            print("message_end_token: ", self.message_end_token)

    @validate_call
    def __discover_message_delimiters(self) -> tuple[str, str]:
        sentinel = "__CALL_ME_MAYBE_SENTINEL__"
        rendered = self._tokenizer.apply_chat_template(
            [
                {
                    "role": ChatMLRole.USER.value,
                    "content": sentinel,
                }
            ],
            tokenize=False,
            add_generation_prompt=False,
        )
        role = ChatMLRole.USER.value
        if isinstance(rendered, str):
            role_index = rendered.index(role)
            sentinel_index = rendered.index(sentinel)

            return (
                    rendered[:role_index],
                    rendered[sentinel_index + len(sentinel):].strip()
                )
        return ("", "")

    @validate_call
    def __split_context(
        self,
        context: list[int],
    ) -> list[list[int]]:
        """
        Recebe uma sequência completa de token_ids (histórico do chat) e separa
        cada mensagem individual utilizando os tokens especiais de início e fim
        descobertos durante a inicialização.

        Exemplo de entrada:

        [
            151644, ..., 151645,
            151644, ..., 151645,
            151644, ..., 151645,
        ]

        Retorno:

        [
            [151644, ..., 151645],
            [151644, ..., 151645],
            [151644, ..., 151645],
        ]
        """

        messages: list[list[int]] = []
        current_message: list[int] = []
        inside_message = False
        for token in context:
            # Encontrou o início de uma nova mensagem.
            # Caso uma mensagem anterior tenha ficado incompleta,
            # ela é descartada e iniciamos uma nova.
            if token == self.message_start_token:
                current_message = [token]
                inside_message = True
                continue
            # Enquanto estivermos dentro de uma mensagem,
            # acumulamos todos os tokens exatamente como foram
            # produzidos pelo modelo/tokenizer.
            if inside_message:
                current_message.append(token)
                # Ao encontrar o delimitador de fim,
                # armazenamos a mensagem completa e
                # voltamos ao estado "fora de mensagem".
                if token == self.message_end_token:
                    messages.append(current_message)
                    current_message = []
                    inside_message = False
        return messages

    @validate_call
    def _parse_context(
        self,
        context: list[int],
    ) -> list[ChatMessage]:
        """_summary_

        Args:
            context (list[int]): _description_

        Returns:
            list[ChatMessage]: _description_
        """    
        messages = self.__split_context(context)
        parsed_messages: list[ChatMessage] = []

        for message_tokens in messages:
            text = self.decode(message_tokens).strip()

            if not text:
                continue
            role, body = text.split(maxsplit=1)
            role = ChatMLRole(role)

            if role is ChatMLRole.SYSTEM:
                parsed_messages.append(
                    SystemMessage(
                        role=role,
                        content=body.strip(),
                    )
                )

            elif role is ChatMLRole.USER:
                parsed_messages.append(
                    UserMessage(
                        role=role,
                        content=body.strip(),
                    )
                )

            elif role is ChatMLRole.TOOL:
                parsed_messages.append(
                    ToolMessage(
                        role=role,
                        content=body.strip(),
                    )
                )

            elif role is ChatMLRole.ASSISTANT:
                think: str | None = None
                tool_calls: list[ToolCall] = []
                think_match = re.search(
                    r"<think>(.*?)</think>",
                    body,
                    flags=re.DOTALL,
                )

                if think_match:
                    think = think_match.group(1).strip()
                    body = (
                        body[:think_match.start()]
                        + body[think_match.end():]
                    )

                for tool_match in re.finditer(
                    r"<tool_call>(.*?)</tool_call>",
                    body,
                    flags=re.DOTALL,
                ):

                    tool_json = tool_match.group(1).strip()

                    data = json.loads(tool_json)

                    tool_calls.append(
                        ToolCall.model_validate(data)
                    )

                body = re.sub(
                    r"<tool_call>.*?</tool_call>",
                    "",
                    body,
                    flags=re.DOTALL,
                ).strip()

                parsed_messages.append(
                    AssistantMessage(
                        role=role,
                        think=think,
                        tool_calls=tool_calls,
                        content=body if body else None,
                    )
                )

        return parsed_messages

    @validate_call
    def bind_functions(
        self,
        function_schemas: list[FunctionDefinition]
    ) -> None:
        """."""
        self.function_schemas.extend([
            func.model_dump(exclude_none=True) for func in function_schemas
        ])

    @validate_call
    def format_prompt(self, messages: list[ChatMessage]) -> str:
        """."""
        formatted_messages = [
            msg.model_dump(exclude_none=True) for msg in messages
        ]
        self._tokenizer.response_parse()
        return_value = self._tokenizer.apply_chat_template(
            formatted_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        if isinstance(return_value, str):
            return return_value
        return ""

    @validate_call
    def format_prompt_with_functions(
        self,
        messages: list[ChatMessage]
    ) -> str:
        """."""
        if len(self.function_schemas) == 0:
            msg = ("call_me_maybe: "
                   "It is necessary to associate function schemas.\n")
            raise Exception(msg)
        # Converter os modelos Pydantic de volta para dicts para
        # o aplicar prompt template
        formatted_messages = [
            msg.model_dump(exclude_none=True) for msg in messages
        ]
        return_value = self._tokenizer.apply_chat_template(
            formatted_messages,
            tools=[*self.function_schemas],
            tokenize=False,
            add_generation_prompt=True
        )
        if isinstance(return_value, str):
            return return_value
        return ""

    @validate_call
    def invoke_calling_function(
        self,
        prompt: str | list[ChatMessage]
    ) -> list[ChatMessage]:
        """;"""
        if len(self.function_schemas) == 0:
            msg = ("call_me_maybe: "
                   "It is necessary to associate function schemas.\n")
            raise Exception(msg)

        if isinstance(prompt, str):
            prompt = cast(
                list[ChatMessage],
                [
                    UserMessage(
                        role=ChatMLRole.USER,
                        content=prompt
                    )
                ]
            )
        formatted_prompt = self.format_prompt_with_functions(prompt)    # já funciona e testado

        input_ids = self.encode(formatted_prompt)

        context: list[int] = input_ids.tolist()[0]
        initial_context_len = len(context)
        if self.verbose_mode:
            print(self.decode(context), end="", flush=True)

        state = GenerationState(
            function_schemas=self.function_schemas,
            tokenizer=self._tokenizer,
        )
        
        restrictor = DFAConstrainedRestrictor(self._tokenizer)
        selector = GreedySelector()

        while True:
            logits = self.get_logits_from_input_ids(context)
            
            restricted_logits = restrictor.restrict(
                logits,
                state,
            )
            next_token_id = selector.select(
                restricted_logits
            )
            
            context.append(next_token_id)
            state.consume(next_token_id)
            
            if self.verbose_mode:
                print(
                    self.decode([next_token_id]),
                    end="",
                    flush=True
                )
            if state.is_finished():
                break
            if len(context) - initial_context_len >= self._max_tokens:
                break
            if next_token_id == self._tokenizer.eos_token_id:
                break
                
        response = self._parse_context(context)
        return response

    # @validate_call
    # def invoke_calling_function(
    #     self,
    #     prompt: str | list[ChatMessage]
    # ) -> list[ChatMessage]:
    #     """;"""
    #     if len(self.function_schemas) == 0:
    #         msg = ("call_me_maybe: "
    #                "It is necessary to associate function schemas.\n")
    #         raise Exception(msg)

    #     if isinstance(prompt, str):
    #         prompt = cast(
    #             list[ChatMessage],
    #             [
    #                 UserMessage(
    #                     role=ChatMLRole.USER,
    #                     content=prompt
    #                 )
    #             ]
    #         )
    #     formatted_prompt = self.format_prompt_with_functions(prompt)    # já funciona e testado

    #     input_ids = self.encode(formatted_prompt)

    #     context: list[int] = input_ids.tolist()[0]
    #     initial_context_len = len(context)
    #     if self.verbose_mode:
    #         print(self.decode(context), end="", flush=True)
    #     context = input_ids.tolist()[0]
    #     state = GenerationState(
    #         function_schemas=self.function_schemas,
    #         tokenizer=self._tokenizer,
    #     )

    #     while True:
    #         logits = self.get_logits_from_input_ids(context)
    #         restricted_logits = self.token_restrictor.restrict(
    #             logits,
    #             state,
    #         )
    #         next_token_id = self.token_selector.select(
    #             restricted_logits
    #         )
    #         context.append(next_token_id)
    #         state.consume(next_token_id)
    #         if self.verbose_mode:
    #             print(
    #                 self.decode([next_token_id]),
    #                 end="",
    #                 flush=True
    #             )
    #         if state.is_finished():
    #             break
    #         if len(context) - initial_context_len >= self._max_tokens:
    #             break
    #     response = self._parse_context(context)
    #     return response

    @validate_call
    def invoke(
        self,
        prompt: str | list[ChatMessage]
    ) -> list[ChatMessage]:
        """."""
        if isinstance(prompt, str):
            prompt = cast(
                list[ChatMessage],
                [
                    UserMessage(
                        role=ChatMLRole.USER,
                        content=prompt
                    )
                ]
            )
        formatted_prompt = self.format_prompt(prompt)

        input_ids = self.encode(formatted_prompt)

        context: list[int] = input_ids.tolist()[0]
        if self.verbose_mode:
            print(self.decode(context), end="", flush=True)

        while True:
            # Obtém a distribuição para o próximo token
            logits = self.get_logits_from_input_ids(context)

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
            if self.verbose_mode:
                print(self.decode([next_token_id]), end="", flush=True)

            # Verifica se terminou
            if next_token_id == self._tokenizer.eos_token_id:
                break

        response = self._parse_context(context)
        return response


    # ? métodos privados para esse fluxo de saída estruturada

    # método de invokar o modelo com saída restrita (estruturada especifica 
    # json etc, receber por parametro qual a restrição)
    # para pode reutilizar para outras coisas, (chamada de pegar parametros, 
    # chamada de reconhecer função, invokar o modelo para obrigar uma saída
    # JSON estruturada especifica)

    # pass

    # método para pegar os logits dos valores restritos de tipo
    #  (BOOLEAN, NUMBER (int e float), STRING, ETC)
    # para cada modelo > tokenizer.encode("true") > obtém os IDs > guarda
    #  internamente

    # para verificar se não for igual, verifica se o estado atual inclui

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

