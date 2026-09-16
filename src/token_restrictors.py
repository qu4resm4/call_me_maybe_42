from abc import ABC, abstractmethod
from typing import Any, List
import numpy as np
from .constraints import GenerationState

class TokenRestrictor(ABC):
    def __init__(self, tokenizer: Any):
        self.tokenizer = tokenizer

    @abstractmethod
    def restrict(self, logits: List[float], state: GenerationState) -> List[float]:
        """
        Aplica restrições aos logits com base no estado da geração.
        Retorna os logits modificados (mascarados).
        """
        pass

class DFAConstrainedRestrictor(TokenRestrictor):
    def restrict(self, logits: List[float], state: GenerationState) -> List[float]:
        # Converte para array para manipular
        logits_arr = np.array(logits)
        
        # Pega os IDs de tokens permitidos para o estado atual
        allowed_token_ids = state.get_allowed_token_ids()
        
        # Se não houver restrições, retorna logits originais
        if not allowed_token_ids:
            return logits
            
        # Cria máscara: -inf para todos
        mask = np.full(logits_arr.shape, -np.inf)
        
        # Preserva os valores originais apenas para os permitidos
        mask[allowed_token_ids] = logits_arr[allowed_token_ids]
        
        return mask.tolist()
