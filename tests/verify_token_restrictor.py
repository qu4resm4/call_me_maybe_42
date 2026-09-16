import numpy as np
from src.token_restrictors import TokenRestrictor
from src.constraints import GenerationState

class NoOpRestrictor(TokenRestrictor):
    def restrict(self, logits: np.ndarray, state: GenerationState) -> np.ndarray:
        return logits

def test_restrictor_loading():
    # Mock tokenizer
    class MockTokenizer:
        pass
    
    tokenizer = MockTokenizer()
    restrictor = NoOpRestrictor(tokenizer)
    
    # Mock logits
    logits = np.array([0.1, 0.2, 0.3])
    # Mock state
    state = GenerationState(function_schemas=[], tokenizer=tokenizer)
    
    restricted_logits = restrictor.restrict(logits, state)
    
    assert np.array_equal(logits, restricted_logits)
    print("TokenRestrictor interface and NoOp implementation loaded and verified!")

if __name__ == "__main__":
    test_restrictor_loading()
