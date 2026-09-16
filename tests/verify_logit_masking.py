import numpy as np
from src.token_restrictors import DFAConstrainedRestrictor
from src.constraints import GenerationState
from src.generation_phase import GenerationPhase

class MockTokenizer:
    def decode(self, ids):
        return ""
    
    def encode(self, text):
        return [0, 1]

class MockGenerationState(GenerationState):
    def get_allowed_token_ids(self) -> list[int]:
        # Permite apenas os tokens de ID 0 e 1
        return [0, 1]

def test_logit_masking():
    tokenizer = MockTokenizer()
    restrictor = DFAConstrainedRestrictor(tokenizer)
    state = MockGenerationState(function_schemas=[], tokenizer=tokenizer)
    
    # Vocabulário de tamanho 5
    logits = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    
    restricted_logits = restrictor.restrict(logits, state)
    
    # Esperado: 
    # Tokens permitidos (0, 1) mantêm valores originais (1.0, 2.0)
    # Tokens proibidos (2, 3, 4) tornam-se -inf
    expected = np.array([1.0, 2.0, -np.inf, -np.inf, -np.inf])
    
    assert np.array_equal(restricted_logits, expected)
    print("Logit masking with -inf verified successfully!")

if __name__ == "__main__":
    test_logit_masking()
