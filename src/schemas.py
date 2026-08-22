# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   schemas.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/22 22:15:08 by gquaresm            #+#    #+#            #
#   Updated: 2026/08/09 13:43:29 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from abc import ABC
from enum import StrEnum
from numbers import Number
from typing import Literal, Any
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
#
#    Program Schemas
#
# -----------------------------------------------------------------------------


class ParameterType(StrEnum):
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"

    @property
    def python_type(self) -> type:
        return {
            ParameterType.INTEGER: int,
            ParameterType.NUMBER: Number,  # na moulinette está float -> number
            ParameterType.STRING: str,
            ParameterType.BOOLEAN: bool,
            ParameterType.ARRAY: list,
            ParameterType.OBJECT: dict,
        }[self]


class ParameterInfo(BaseModel):
    type: ParameterType


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, ParameterInfo]
    returns: ParameterInfo


class PromptInput(BaseModel):
    prompt: str


class FunctionCallingResult(BaseModel):
    prompt: str
    name: str
    parameters: dict[str, ParameterInfo]

# -----------------------------------------------------------------------------
#
#    My SDK Schemas
#
# -----------------------------------------------------------------------------

# tipar resposta normal?
# tipar resposta calling function
# tipar schema de resposta estrutura ? vai dar trabalho não fazer
#  isso depende de um leitor de estrutura e criação dinamica


class ChatMLRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel, ABC):
    pass


class SystemMessage(ChatMessage):
    role: Literal[ChatMLRole.SYSTEM]
    content: str


class UserMessage(ChatMessage):
    role: Literal[ChatMLRole.USER]
    content: str


class ToolCall(ChatMessage):
    name: str
    arguments: dict[str, Any]


class AssistantMessage(ChatMessage):
    role: Literal[ChatMLRole.ASSISTANT]
    content: str | None = None
    think: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)


class ToolMessage(ChatMessage):
    role: Literal[ChatMLRole.TOOL]
    content: str
