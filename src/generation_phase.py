from enum import StrEnum


class GenerationPhase(StrEnum):
    PASSTHROUGH = "passthrough"
    START = "start"
    OPEN_TOOL_TAG = "open_tool_tag"
    OPEN_JSON_BRACE = "open_json_brace"
    KEY_NAME_START = "key_name_start"
    KEY_NAME_CONTENT = "key_name_content"
    KEY_NAME_END = "key_name_end"
    COLON_1 = "colon_1"
    VALUE_NAME_START = "value_name_start"
    VALUE_NAME_CONTENT = "value_name_content"
    VALUE_NAME_END = "value_name_end"
    COMMA = "comma"
    KEY_ARGS_START = "key_args_start"
    KEY_ARGS_CONTENT = "key_args_content"
    KEY_ARGS_END = "key_args_end"
    COLON_2 = "colon_2"
    ARGS_VALUE_CONTENT = "args_value_content"
    CLOSE_JSON_BRACE = "close_json_brace"
    CLOSE_TOOL_TAG = "close_tool_tag"
    FINISHED = "finished"
