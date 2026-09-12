from typing import Any, Optional
from .generation_phase import GenerationPhase

class GenerationState:
    def __init__(self, function_schemas: list, tokenizer: Any):
        self.function_schemas = function_schemas
        self.tokenizer = tokenizer
        self.current_phase = GenerationPhase.START
        
        # Robust buffers for parsing
        self.function_buffer = ""
        self.parameter_buffer = ""
        self.value_buffer = ""
        
    def consume(self, token_id: int):
        # Decode the token
        token_str = self.tokenizer.decode([token_id])
        
        # Update phase and buffers based on token content
        self._update_state(token_str)
        
    def _update_state(self, token_str: str):
        # Refactored transition logic based on phase and token content
        if self.current_phase == GenerationPhase.START:
            if "{" in token_str:
                self.current_phase = GenerationPhase.FUNCTION_KEY
        
        elif self.current_phase == GenerationPhase.FUNCTION_KEY:
            self.function_buffer += token_str
            # Transition logic will be refined to match schema constraints
            if '"function"' in self.function_buffer:
                self.current_phase = GenerationPhase.FUNCTION_VALUE
                self.function_buffer = ""
        
        # Additional phase transitions...
        
    def is_finished(self) -> bool:
        return self.current_phase == GenerationPhase.FINISHED
