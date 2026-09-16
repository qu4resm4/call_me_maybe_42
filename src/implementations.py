from typing import Any
import torch
from src.token_restrictors import TokenRestrictor
from src.token_selectors import TokenSelector

class GreedySelector(TokenSelector):
    def select(self, logits: Any) -> int:
        if not isinstance(logits, torch.Tensor):
            logits = torch.tensor(logits)
        return int(torch.argmax(logits))

class NoOpRestrictor(TokenRestrictor):
    def restrict(self, logits: torch.Tensor, state: Any) -> torch.Tensor:
        return logits
