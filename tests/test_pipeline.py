import pytest
from pathlib import Path
from src.llm_sdk_calling_function import Model_with_Calling_Function
from src.schemas import FunctionDefinition, ParameterInfo, ParameterType

def test_function_calling_with_constraints():
    # Setup
    model_name = "Qwen/Qwen3-0.6B" # Usando o default do projeto
    llm = Model_with_Calling_Function(model_name, verbose_mode=False)
    
    # Define a simple function schema
    schema = FunctionDefinition(
        name="get_weather",
        description="Gets the current weather for a location.",
        parameters={
            "location": ParameterInfo(type=ParameterType.STRING)
        },
        returns=ParameterInfo(type=ParameterType.STRING)
    )
    llm.bind_functions([schema])
    
    # Run
    prompt = "What's the weather in Rio?"
    response = llm.invoke_calling_function(prompt)
    
    # Assert
    assert len(response) > 0
    # Verifica se a última mensagem é do assistente e contém uma tool_call
    assistant_msg = response[-1]
    assert hasattr(assistant_msg, 'tool_calls')
    assert len(assistant_msg.tool_calls) > 0
    assert assistant_msg.tool_calls[0].name == "get_weather"
