# ########################################################################### #
#   shebang: 0                                                                #
#                                                          :::      ::::::::  #
#   schemas.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: gquaresm <gquaresm@student.42.rio>           +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/22 22:15:08 by gquaresm            #+#    #+#            #
#   Updated: 2026/07/23 09:33:57 by gquaresm           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from enum import StrEnum
from numbers import Number
from pydantic import BaseModel


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
