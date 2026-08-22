class TokenRestrictor:
    def restrict(
        self,
        logits: list[float],
        state: GenerationState
    ) -> list[float]:
        ...

# TokenRestrictor
#       │
#       ▼
# Constraint/DFA
#       │
#       ▼
# quais tokens são válidos?
#       │
#       ▼
# mask logits

# next_token_id = token_selector.select(logits)