"""Independent token-selection and token-restriction strategies."""

from collections.abc import Callable, Sequence

from pydantic import BaseModel, ConfigDict


class TokenSelectionError(ValueError):
    """Raised when no token can be selected from a masked distribution."""


class TokenSelector(BaseModel):
    """Base Pydantic model for a token selection strategy."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def select(self, logits: Sequence[float], allowed_tokens: set[int]) -> int:
        """Select one token id from the allowed logits."""
        raise NotImplementedError

    def select_valid(
        self,
        logits: Sequence[float],
        vocabulary: dict[int, str],
        prefix: str,
        is_valid_prefix: Callable[[str], bool],
        excluded_tokens: set[int],
    ) -> tuple[int, int]:
        """Select the best token accepted by a prefix validator."""
        raise NotImplementedError


class GreedyTokenSelector(TokenSelector):
    """Choose the highest-logit token among allowed ids."""

    def select(self, logits: Sequence[float], allowed_tokens: set[int]) -> int:
        """Return the allowed token with the highest logit."""
        if not allowed_tokens:
            raise TokenSelectionError("the grammar has no valid next token")
        return max(allowed_tokens, key=lambda token_id: logits[token_id])

    def select_valid(
        self,
        logits: Sequence[float],
        vocabulary: dict[int, str],
        prefix: str,
        is_valid_prefix: Callable[[str], bool],
        excluded_tokens: set[int],
    ) -> tuple[int, int]:
        """Return the highest-logit token that preserves the grammar."""
        ranked_ids = sorted(
            range(len(logits)),
            key=lambda token_id: logits[token_id],
            reverse=True,
        )
        checked = 0
        for token_id in ranked_ids:
            if token_id in excluded_tokens or not vocabulary.get(token_id):
                continue
            checked += 1
            if is_valid_prefix(prefix + vocabulary[token_id]):
                return token_id, checked
        raise TokenSelectionError("the grammar has no valid next token")


class TokenRestrictor(BaseModel):
    """Base Pydantic model for a token restriction strategy."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def allowed_tokens(
        self,
        prefix: str,
        vocabulary: dict[int, str],
        special_token_ids: set[int],
    ) -> set[int]:
        """Return token ids that preserve a valid generation prefix."""
        raise NotImplementedError
