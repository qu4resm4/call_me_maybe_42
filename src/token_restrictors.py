from abc import ABC, abstractmethod
from typing import List, Any
import numpy as np
from .generation_phase import GenerationPhase
from .constraints import GenerationState

class TokenRestrictor(ABC):
    @abstractmethod
    def restrict(
        self,
        logits: List[float],
        state: Any
    ) -> List[float]:
        pass

class DFAConstraintRestrictor(TokenRestrictor):
    def restrict(
        self,
        logits: List[float],
        state: GenerationState
    ) -> List[float]:
        # Convert logits to numpy array for easier manipulation
        logits_arr = np.array(logits, dtype=np.float32)

        # Mask tokens based on the current state.
        # This is a placeholder for the actual masking logic
        # based on the function schemas and current phase.

        if state.current_phase == GenerationPhase.FUNCTION_KEY:
            # Logic to mask tokens that are not valid keys for the next step
            pass

        # Example: mask all tokens with -inf
        # logits_arr[invalid_indices] = -float('inf')

        return logits_arr.tolist()

class NoRestrictionTokenRestrictor(TokenRestrictor):
    def restrict(
        self,
        logits: List[float],
        state: Any
    ) -> List[float]:
        # Return logits as is
        return logits