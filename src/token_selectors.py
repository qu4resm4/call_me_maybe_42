from abc import ABC, abstractmethod
import torch

class TokenSelector(ABC):
    @abstractmethod
    def select(self, logits: torch.Tensor) -> int:
        pass
