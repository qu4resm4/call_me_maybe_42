from enum import StrEnum


class GenerationPhase(StrEnum):
    START = "start"
    FUNCTION_KEY = "function_key"
    FUNCTION_VALUE = "function_value"
    ARGUMENTS_KEY = "arguments_key"
    ARGUMENTS_VALUE = "arguments_value"
    PARAMETER_KEY = "parameter_key"
    PARAMETER_VALUE = "parameter_value"
    FINISHED = "finished"
