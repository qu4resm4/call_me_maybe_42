import pytest
from src.constraints import GenerationState
from src.generation_phase import GenerationPhase

class MockTokenizer:
    def decode(self, ids):
        mapping = {1: "{", 2: '"key"', 3: ":", 4: "val", 5: ",", 6: "}", 7: '"arg"', 8: ":", 9: "argval"}
        return "".join([mapping.get(i, "") for i in ids])
    
    def encode(self, text):
        mapping = {"{": [1], '"tool_calls"': [2]}
        return mapping.get(text, [0])

def test_generation_state_transitions():
    tokenizer = MockTokenizer()
    state = GenerationState(function_schemas=[], tokenizer=tokenizer)
    
    assert state.current_phase == GenerationPhase.START
    
    # Simulate: {
    state.consume(1)
    assert state.current_phase == GenerationPhase.FUNCTION_KEY
    
    # Simulate: "key":
    state.consume(3)
    assert state.current_phase == GenerationPhase.FUNCTION_VALUE
    
    # Simulate: ,
    state.consume(5)
    assert state.current_phase == GenerationPhase.ARGUMENTS_KEY
    
    # Simulate: "arg":
    state.consume(8)
    assert state.current_phase == GenerationPhase.ARGUMENTS_VALUE
    
    # Simulate: }
    state.consume(6)
    assert state.current_phase == GenerationPhase.FINISHED
    assert state.is_finished()

if __name__ == "__main__":
    test_generation_state_transitions()
    print("Test passed!")
