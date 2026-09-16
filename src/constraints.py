from typing import Any, List
from .generation_phase import GenerationPhase

class GenerationState:
    def __init__(self, function_schemas: list, tokenizer: Any):
        self.function_schemas = function_schemas
        self.tokenizer = tokenizer
        self.current_phase = GenerationPhase.PASSTHROUGH
        
        self.buffer = ""
        self._precompute_allowed_tokens()
        
    def _precompute_allowed_tokens(self):
        # Mapeia cada fase para os tokens que a iniciam ou permitem a progressão.
        self.allowed_tokens = {
            GenerationPhase.OPEN_TOOL_TAG: self.tokenizer.encode("{"),
            GenerationPhase.OPEN_JSON_BRACE: self.tokenizer.encode('"'),
            GenerationPhase.KEY_NAME_START: self.tokenizer.encode('n'),
            GenerationPhase.KEY_NAME_CONTENT: self.tokenizer.encode('"'),
            GenerationPhase.KEY_NAME_END: self.tokenizer.encode(':'),
            GenerationPhase.COLON_1: self.tokenizer.encode('"'),
            GenerationPhase.VALUE_NAME_START: self.tokenizer.encode('a'),
            GenerationPhase.VALUE_NAME_CONTENT: self.tokenizer.encode('"'),
            GenerationPhase.VALUE_NAME_END: self.tokenizer.encode(','),
            GenerationPhase.COMMA: self.tokenizer.encode('"'),
            GenerationPhase.KEY_ARGS_START: self.tokenizer.encode('a'),
            GenerationPhase.KEY_ARGS_CONTENT: self.tokenizer.encode('"'),
            GenerationPhase.KEY_ARGS_END: self.tokenizer.encode(':'),
            GenerationPhase.COLON_2: self.tokenizer.encode('{'),
            GenerationPhase.ARGS_VALUE_CONTENT: self.tokenizer.encode('}'),
            GenerationPhase.CLOSE_JSON_BRACE: self.tokenizer.encode(">"),
        }

    def consume(self, token_id: int):
        token_str = self.tokenizer.decode([token_id])
        self.update_phase_by_buffer(token_str)
        
    def update_phase_by_buffer(self, token_str: str):
        old_phase = self.current_phase
        self.buffer += token_str
        
        # Lógica de transição de fase baseada no buffer e delimitadores JSON/XML
        
        if self.current_phase == GenerationPhase.PASSTHROUGH:
            if "<tool_call>" in self.buffer:
                self.current_phase = GenerationPhase.OPEN_TOOL_TAG
                self.buffer = ""
                
        elif self.current_phase == GenerationPhase.OPEN_TOOL_TAG:
            if "{" in self.buffer:
                self.current_phase = GenerationPhase.OPEN_JSON_BRACE
                self.buffer = "{"
        
        elif self.current_phase == GenerationPhase.OPEN_JSON_BRACE:
            if '"' in self.buffer:
                self.current_phase = GenerationPhase.KEY_NAME_START
        
        elif self.current_phase == GenerationPhase.KEY_NAME_START:
            if "name" in self.buffer:
                self.current_phase = GenerationPhase.KEY_NAME_CONTENT
            elif '"' in self.buffer:
                self.current_phase = GenerationPhase.KEY_NAME_END
        
        elif self.current_phase == GenerationPhase.KEY_NAME_CONTENT:
            if '"' in self.buffer:
                self.current_phase = GenerationPhase.KEY_NAME_END
                
        elif self.current_phase == GenerationPhase.KEY_NAME_END:
            if ":" in self.buffer:
                self.current_phase = GenerationPhase.COLON_1
        
        elif self.current_phase == GenerationPhase.COLON_1:
            if '"' in self.buffer:
                self.current_phase = GenerationPhase.VALUE_NAME_START
        
        elif self.current_phase == GenerationPhase.VALUE_NAME_START:
            # Aqui deveríamos validar contra os nomes de funções em self.function_schemas
            self.current_phase = GenerationPhase.VALUE_NAME_CONTENT
            
        elif self.current_phase == GenerationPhase.VALUE_NAME_CONTENT:
            if '"' in self.buffer:
                self.current_phase = GenerationPhase.VALUE_NAME_END
        
        elif self.current_phase == GenerationPhase.VALUE_NAME_END:
            if "," in self.buffer:
                self.current_phase = GenerationPhase.COMMA
                
        elif self.current_phase == GenerationPhase.COMMA:
            if '"' in self.buffer:
                self.current_phase = GenerationPhase.KEY_ARGS_START
        
        elif self.current_phase == GenerationPhase.KEY_ARGS_START:
            if "arguments" in self.buffer:
                self.current_phase = GenerationPhase.KEY_ARGS_CONTENT
            elif '"' in self.buffer:
                self.current_phase = GenerationPhase.KEY_ARGS_END

        elif self.current_phase == GenerationPhase.KEY_ARGS_CONTENT:
            if '"' in self.buffer:
                self.current_phase = GenerationPhase.KEY_ARGS_END
        
        elif self.current_phase == GenerationPhase.KEY_ARGS_END:
            if ":" in self.buffer:
                self.current_phase = GenerationPhase.COLON_2
        
        elif self.current_phase == GenerationPhase.COLON_2:
            self.current_phase = GenerationPhase.ARGS_VALUE_CONTENT

        elif self.current_phase == GenerationPhase.ARGS_VALUE_CONTENT:
            # Lógica para fechar JSON: contar chaves ou esperar '}'
            if "}" in self.buffer:
                self.current_phase = GenerationPhase.CLOSE_JSON_BRACE
                
        elif self.current_phase == GenerationPhase.CLOSE_JSON_BRACE:
            if ">" in self.buffer:
                self.current_phase = GenerationPhase.CLOSE_TOOL_TAG
                self.current_phase = GenerationPhase.FINISHED

        # if old_phase != self.current_phase:
        #     print(f"--- [FSM] Transição de {old_phase} para {self.current_phase} ---")

    def is_finished(self) -> bool:
        return self.current_phase == GenerationPhase.FINISHED
    
    def get_allowed_token_ids(self) -> List[int]:
        if self.current_phase == GenerationPhase.PASSTHROUGH:
            return [] # Permitir tudo
        
        # Para evitar loops, se a fase não tiver tokens definidos, 
        # permitimos tudo por enquanto (não restringimos).
        allowed = self.allowed_tokens.get(self.current_phase, [])
        if not allowed:
            return [] # Permitir tudo se não houver restrição
        
        return allowed
